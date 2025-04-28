"""
Gerenciador de Regras

Este módulo implementa um gerenciador para as regras de resposta automática,
permitindo carregar, adicionar e gerenciar regras de resposta.
"""

import os
import json
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

# Configurar logging
logger = logging.getLogger(__name__)

class RuleManager:
    """
    Classe para gerenciar regras de resposta automática.
    """
    
    def __init__(self, db_session=None, rules_file='data/rules.json'):
        """
        Inicializa o gerenciador de regras.
        
        Args:
            db_session: Sessão do SQLAlchemy para acesso ao banco de dados
            rules_file (str): Caminho para o arquivo JSON de regras alternativo
        """
        self.db_session = db_session
        self.rules_file = rules_file
        self.rules_dict = {}
        self.last_update = None
        
        # Carregar regras
        self.load_rules()
    
    def load_rules(self):
        """
        Carrega regras do banco de dados ou arquivo JSON.
        
        Returns:
            dict: Dicionário com as regras carregadas
        """
        # Tentar carregar do banco de dados primeiro
        if self.db_session:
            try:
                from models import Rule
                
                db_rules = self.db_session.query(Rule).filter_by(is_active=True).all()
                
                # Limpar regras existentes
                self.rules_dict.clear()
                
                # Adicionar regras do banco de dados
                for rule in db_rules:
                    self.rules_dict[rule.keyword] = rule.response
                
                self.last_update = datetime.now()
                logger.info(f"Carregadas {len(self.rules_dict)} regras do banco de dados")
                
                return self.rules_dict
                
            except Exception as e:
                logger.error(f"Erro ao carregar regras do banco de dados: {str(e)}")
                logger.info("Tentando carregar do arquivo de regras...")
        
        # Se não conseguiu carregar do banco de dados, tenta do arquivo
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    rules_data = json.load(f)
                
                # Limpar regras existentes
                self.rules_dict.clear()
                
                # Adicionar regras do arquivo
                for rule in rules_data:
                    if 'palavra_chave' in rule and 'resposta' in rule:
                        self.rules_dict[rule['palavra_chave']] = rule['resposta']
                
                self.last_update = datetime.now()
                logger.info(f"Carregadas {len(self.rules_dict)} regras do arquivo {self.rules_file}")
            else:
                # Arquivo não existe, usar regras padrão
                self._load_default_rules()
                
        except Exception as e:
            logger.error(f"Erro ao carregar regras do arquivo: {str(e)}")
            # Usar regras padrão
            self._load_default_rules()
        
        return self.rules_dict
    
    def _load_default_rules(self):
        """Carrega regras padrão quando não há outra fonte disponível."""
        self.rules_dict = {
            "orçamento": ("Obrigado por solicitar um orçamento. "
                         "Para podermos atendê-lo melhor, precisamos das seguintes informações:\n\n"
                         "1. Descrição detalhada do produto/serviço desejado\n"
                         "2. Quantidade necessária\n"
                         "3. Data de entrega desejada\n\n"
                         "Assim que recebermos essas informações, enviaremos seu orçamento em até 24 horas úteis."),
            
            "suporte": ("Recebemos sua solicitação de suporte técnico. "
                       "Um de nossos especialistas irá analisar seu caso em breve.\n\n"
                       "Para agilizar o atendimento, informe:\n"
                       "- Número de série do produto (se aplicável)\n"
                       "- Descrição detalhada do problema\n"
                       "- Capturas de tela do erro (se possível)\n\n"
                       "Nosso horário de atendimento é de segunda a sexta, das 8h às 18h.")
        }
        
        self.last_update = datetime.now()
        logger.info(f"Carregadas {len(self.rules_dict)} regras padrão")
    
    def save_rules(self):
        """
        Salva regras no arquivo JSON.
        
        Returns:
            bool: True se o salvamento foi bem-sucedido, False caso contrário
        """
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
            
            # Converter para o formato de lista
            rules_list = [
                {"palavra_chave": palavra_chave, "resposta": resposta}
                for palavra_chave, resposta in self.rules_dict.items()
            ]
            
            # Salvar no arquivo
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(rules_list, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Regras salvas em {self.rules_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar regras: {str(e)}")
            return False
    
    def add_rule(self, keyword, response):
        """
        Adiciona uma nova regra.
        
        Args:
            keyword (str): Palavra-chave para correspondência
            response (str): Resposta para a palavra-chave
            
        Returns:
            bool: True se a adição foi bem-sucedida, False caso contrário
        """
        try:
            # Adicionar ao dicionário em memória
            self.rules_dict[keyword] = response
            
            # Adicionar ao banco de dados, se disponível
            if self.db_session:
                try:
                    from models import Rule
                    
                    # Verificar se já existe
                    existing_rule = self.db_session.query(Rule).filter_by(keyword=keyword).first()
                    
                    if existing_rule:
                        # Atualizar regra existente
                        existing_rule.response = response
                        existing_rule.is_active = True
                        existing_rule.updated_at = datetime.now()
                    else:
                        # Criar nova regra
                        new_rule = Rule(
                            keyword=keyword,
                            response=response,
                            is_active=True
                        )
                        self.db_session.add(new_rule)
                    
                    self.db_session.commit()
                    logger.info(f"Regra para '{keyword}' salva no banco de dados")
                    
                except SQLAlchemyError as e:
                    logger.error(f"Erro ao salvar regra no banco de dados: {str(e)}")
                    self.db_session.rollback()
                    # Continue para salvar no arquivo
            
            # Salvar no arquivo
            self.save_rules()
            
            self.last_update = datetime.now()
            logger.info(f"Regra adicionada/atualizada para a palavra-chave: '{keyword}'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao adicionar regra: {str(e)}")
            return False
    
    def remove_rule(self, keyword):
        """
        Remove uma regra.
        
        Args:
            keyword (str): Palavra-chave a ser removida
            
        Returns:
            bool: True se a remoção foi bem-sucedida, False caso contrário
        """
        try:
            # Remover do dicionário em memória
            if keyword in self.rules_dict:
                del self.rules_dict[keyword]
            
            # Remover do banco de dados, se disponível
            if self.db_session:
                try:
                    from models import Rule
                    
                    rule = self.db_session.query(Rule).filter_by(keyword=keyword).first()
                    
                    if rule:
                        rule.is_active = False
                        rule.updated_at = datetime.now()
                        self.db_session.commit()
                        logger.info(f"Regra para '{keyword}' desativada no banco de dados")
                    
                except SQLAlchemyError as e:
                    logger.error(f"Erro ao desativar regra no banco de dados: {str(e)}")
                    self.db_session.rollback()
                    # Continue para salvar no arquivo
            
            # Salvar no arquivo
            self.save_rules()
            
            self.last_update = datetime.now()
            logger.info(f"Regra removida para a palavra-chave: '{keyword}'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover regra: {str(e)}")
            return False
    
    def get_rules(self):
        """
        Obtém todas as regras.
        
        Returns:
            dict: Dicionário com as regras
        """
        return self.rules_dict
    
    def reload_rules(self, force=False):
        """
        Recarrega as regras se necessário.
        
        Args:
            force (bool): Se True, força o recarregamento mesmo que não seja necessário
            
        Returns:
            dict: Dicionário com as regras atualizadas
        """
        # Se forçado ou não houver atualização anterior, recarregar
        if force or not self.last_update:
            return self.load_rules()
        
        # Verificar se o banco de dados foi atualizado (se disponível)
        if self.db_session:
            try:
                from models import Rule
                
                latest_rule = self.db_session.query(Rule).order_by(Rule.updated_at.desc()).first()
                
                if latest_rule and latest_rule.updated_at > self.last_update:
                    logger.info("Detectada atualização nas regras do banco de dados")
                    return self.load_rules()
                    
            except Exception as e:
                logger.error(f"Erro ao verificar atualizações de regras: {str(e)}")
        
        # Verificar se o arquivo foi atualizado
        if os.path.exists(self.rules_file):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(self.rules_file))
            
            if file_mtime > self.last_update:
                logger.info("Detectada atualização no arquivo de regras")
                return self.load_rules()
        
        return self.rules_dict 