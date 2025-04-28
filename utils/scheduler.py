"""
Módulo de Agendamento

Este módulo implementa funcionalidades para agendamento de tarefas,
como verificação periódica de novos e-mails.
"""

import time
import threading
import logging
import schedule
from datetime import datetime

# Configurar logging
logger = logging.getLogger(__name__)

class EmailScheduler:
    """
    Classe para agendar e executar verificações periódicas de e-mail.
    """
    
    def __init__(self, interval_minutes=5, start_immediately=True):
        """
        Inicializa o agendador.
        
        Args:
            interval_minutes (int): Intervalo entre verificações em minutos
            start_immediately (bool): Se True, inicia o agendamento imediatamente
        """
        self.interval_minutes = interval_minutes
        self.running = False
        self.scheduler_thread = None
        self.callback = None
        
        if start_immediately:
            self.start()
    
    def _run_continuously(self):
        """Executa o agendador em um loop contínuo."""
        self.running = True
        
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def _job(self):
        """Função executada a cada intervalo agendado."""
        if self.callback:
            try:
                logger.info(f"Executando verificação agendada em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.callback()
            except Exception as e:
                logger.error(f"Erro ao executar tarefa agendada: {str(e)}")
        else:
            logger.warning("Tarefa agendada executada, mas nenhum callback foi definido")
    
    def start(self):
        """Inicia o agendador em uma thread separada."""
        if self.running:
            logger.warning("Agendador já está em execução")
            return False
        
        try:
            # Limpar agendamentos anteriores
            schedule.clear()
            
            # Agendar a execução periódica
            schedule.every(self.interval_minutes).minutes.do(self._job)
            
            # Iniciar thread do agendador
            self.scheduler_thread = threading.Thread(target=self._run_continuously)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            logger.info(f"Agendador iniciado com intervalo de {self.interval_minutes} minutos")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar agendador: {str(e)}")
            self.running = False
            return False
    
    def stop(self):
        """Para o agendador."""
        if not self.running:
            logger.warning("Agendador não está em execução")
            return
        
        try:
            self.running = False
            schedule.clear()
            
            # Aguardar a thread do agendador terminar (com timeout)
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("Agendador parado")
            
        except Exception as e:
            logger.error(f"Erro ao parar agendador: {str(e)}")
    
    def set_callback(self, callback_function):
        """
        Define a função de callback a ser executada a cada intervalo.
        
        Args:
            callback_function: Função a ser executada
        """
        self.callback = callback_function
        logger.info("Função de callback definida")
    
    def set_interval(self, minutes):
        """
        Altera o intervalo entre verificações.
        
        Args:
            minutes (int): Novo intervalo em minutos
        """
        if minutes < 1:
            logger.warning(f"Intervalo inválido ({minutes} minutos). Usando 1 minuto.")
            minutes = 1
        
        self.interval_minutes = minutes
        
        # Reiniciar o agendador com o novo intervalo
        if self.running:
            was_running = True
            self.stop()
        else:
            was_running = False
        
        if was_running:
            self.start()
            
        logger.info(f"Intervalo alterado para {self.interval_minutes} minutos")
    
    def run_now(self):
        """
        Executa a tarefa agendada imediatamente, fora do agendamento.
        
        Returns:
            bool: True se a execução foi bem-sucedida, False caso contrário
        """
        if not self.callback:
            logger.warning("Tentativa de execução imediata, mas nenhum callback foi definido")
            return False
        
        try:
            logger.info("Executando verificação imediata")
            self._job()
            return True
        except Exception as e:
            logger.error(f"Erro ao executar verificação imediata: {str(e)}")
            return False
    
    def is_running(self):
        """
        Verifica se o agendador está em execução.
        
        Returns:
            bool: True se o agendador estiver em execução, False caso contrário
        """
        return self.running and (self.scheduler_thread and self.scheduler_thread.is_alive()) 