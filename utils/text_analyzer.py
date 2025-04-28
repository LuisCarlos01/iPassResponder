"""
Módulo de Análise de Texto

Este módulo implementa funcionalidades para analisar o conteúdo de e-mails
usando NLTK (Natural Language Toolkit) para detecção de palavras-chave.
"""

import re
import logging
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer  # Stemmer para português
from nltk.metrics.distance import edit_distance
import string
from difflib import SequenceMatcher

# Configurar logging
logger = logging.getLogger(__name__)

# Baixar recursos do NLTK na primeira execução
def download_nltk_resources():
    """Baixa os recursos necessários do NLTK."""
    try:
        resources = [
            'punkt',
            'stopwords',
            'rslp'
        ]
        
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                nltk.download(resource, quiet=True)
                
        logger.info("Recursos NLTK verificados/baixados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao baixar recursos NLTK: {str(e)}")
        logger.warning("Continuando sem recursos completos do NLTK")


class TextAnalyzer:
    """
    Classe para análise de texto e correspondência de padrões em e-mails.
    """
    
    def __init__(self, language='portuguese', similarity_threshold=0.7):
        """
        Inicializa o analisador de texto.
        
        Args:
            language (str): Idioma para stopwords ('portuguese' ou 'english')
            similarity_threshold (float): Limiar de similaridade (0.0 a 1.0)
        """
        # Garantir que os recursos NLTK estejam disponíveis
        download_nltk_resources()
        
        self.language = language
        self.similarity_threshold = similarity_threshold
        
        # Carregar stopwords para o idioma especificado
        try:
            self.stop_words = set(stopwords.words(language))
        except:
            logger.warning(f"Stopwords para {language} não disponíveis. Usando conjunto vazio.")
            self.stop_words = set()
            
        # Inicializar stemmer para português
        try:
            self.stemmer = RSLPStemmer()
        except:
            logger.warning("RSLPStemmer não disponível. A stemização não será aplicada.")
            self.stemmer = None
    
    def preprocess_text(self, text):
        """
        Pré-processa o texto para análise.
        
        Args:
            text (str): Texto a ser processado
            
        Returns:
            list: Lista de tokens processados
        """
        if not text:
            return []
            
        # Converter para minúsculas
        text = text.lower()
        
        # Remover caracteres especiais e números
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenizar
        tokens = word_tokenize(text, language=self.language)
        
        # Remover stopwords
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Aplicar stemming se disponível
        if self.stemmer:
            tokens = [self.stemmer.stem(token) for token in tokens]
            
        return tokens
    
    def calculate_similarity(self, text, keyword):
        """
        Calcula a similaridade entre o texto e uma palavra-chave.
        
        Args:
            text (str): Texto a ser analisado
            keyword (str): Palavra-chave para comparação
            
        Returns:
            float: Pontuação de similaridade (0.0 a 1.0)
        """
        # Para correspondência exata
        if keyword.lower() in text.lower():
            return 1.0
            
        # Pré-processar texto e palavra-chave
        text_tokens = self.preprocess_text(text)
        keyword_tokens = self.preprocess_text(keyword)
        
        if not text_tokens or not keyword_tokens:
            return 0.0
        
        # Verificar cada token do texto contra cada token da palavra-chave
        max_similarities = []
        
        for k_token in keyword_tokens:
            if not k_token:
                continue
                
            token_similarities = []
            
            for t_token in text_tokens:
                if not t_token:
                    continue
                    
                # Calcular similaridade de sequência
                similarity = SequenceMatcher(None, k_token, t_token).ratio()
                
                # Considerar também distância de edição para palavras curtas
                if len(k_token) <= 5 or len(t_token) <= 5:
                    max_len = max(len(k_token), len(t_token))
                    if max_len > 0:
                        edit_sim = 1.0 - (edit_distance(k_token, t_token) / max_len)
                        similarity = max(similarity, edit_sim)
                
                token_similarities.append(similarity)
            
            if token_similarities:
                max_similarities.append(max(token_similarities))
        
        # Retornar a média das melhores correspondências para cada token da palavra-chave
        if max_similarities:
            return sum(max_similarities) / len(max_similarities)
        else:
            return 0.0
    
    def find_matching_keywords(self, text, keywords_dict, return_scores=False):
        """
        Encontra palavras-chave correspondentes no texto.
        
        Args:
            text (str): Texto a ser analisado
            keywords_dict (dict): Dicionário de palavras-chave -> respostas
            return_scores (bool): Se True, retorna também as pontuações
            
        Returns:
            list: Lista de palavras-chave correspondentes
            ou
            list: Lista de tuplas (palavra-chave, pontuação) se return_scores=True
        """
        matches = []
        
        for keyword in keywords_dict.keys():
            similarity = self.calculate_similarity(text, keyword)
            
            if similarity >= self.similarity_threshold:
                if return_scores:
                    matches.append((keyword, similarity))
                else:
                    matches.append(keyword)
        
        # Ordenar por pontuação de similaridade (decrescente)
        if return_scores:
            matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches 