"""
Email Response Rules Module

This module defines the rules for automated email responses and the logic
to generate appropriate responses based on email content.
"""

import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define default response rules
# Each rule consists of a keyword to match and the corresponding response
REGRAS = [
    {
        "palavra_chave": "orçamento",
        "resposta": ("Obrigado por solicitar um orçamento. "
                    "Para podermos atendê-lo melhor, precisamos das seguintes informações:\n\n"
                    "1. Descrição detalhada do produto/serviço desejado\n"
                    "2. Quantidade necessária\n"
                    "3. Data de entrega desejada\n\n"
                    "Assim que recebermos essas informações, enviaremos seu orçamento em até 24 horas úteis.")
    },
    {
        "palavra_chave": "suporte",
        "resposta": ("Recebemos sua solicitação de suporte técnico. "
                    "Um de nossos especialistas irá analisar seu caso em breve.\n\n"
                    "Para agilizar o atendimento, informe:\n"
                    "- Número de série do produto (se aplicável)\n"
                    "- Descrição detalhada do problema\n"
                    "- Capturas de tela do erro (se possível)\n\n"
                    "Nosso horário de atendimento é de segunda a sexta, das 8h às 18h.")
    }
]

# Default generic response
RESPOSTA_GENERICA = ("Olá! Recebemos sua mensagem. Em breve retornaremos com mais informações. "
                     "Caso queira agilizar o atendimento, envie seu CPF e o assunto da dúvida.")

def gerar_resposta_assistente(assunto, corpo, return_matched=False):
    """
    Generate an automated response based on email content and predefined rules.
    
    Args:
        assunto (str): The email subject
        corpo (str): The email body content
        return_matched (bool): Whether to return the matched rule keyword
        
    Returns:
        If return_matched is False:
            str: The appropriate response message
        If return_matched is True:
            tuple: (response message, matched rule keyword or None)
    """
    # Combine subject and body for analysis
    conteudo_completo = f"{assunto} {corpo}".lower()
    
    # Track if we've found a matching rule
    resposta_encontrada = False
    resposta_final = ""
    matched_keyword = None
    
    # Check each rule against the content
    for regra in REGRAS:
        palavra_chave = regra["palavra_chave"].lower()
        
        # Use regex to find word boundaries to avoid partial matches
        if re.search(r'\b' + re.escape(palavra_chave) + r'\b', conteudo_completo):
            logger.info(f"Rule matched: '{palavra_chave}'")
            
            # If this is the first match, use the response directly
            if not resposta_encontrada:
                resposta_final = regra["resposta"]
                resposta_encontrada = True
                matched_keyword = regra["palavra_chave"]
            # For additional matches, append to the response
            else:
                resposta_final += f"\n\nTambém notei que você mencionou '{palavra_chave}': {regra['resposta']}"
    
    # If no rule matched, use the generic response
    if not resposta_encontrada:
        logger.info("No specific rule matched. Using generic response.")
        resposta_final = RESPOSTA_GENERICA
    
    # Add a signature to the response
    resposta_final += "\n\nAtenciosamente,\nAssistente Automático"
    
    if return_matched:
        return resposta_final, matched_keyword
    else:
        return resposta_final

def adicionar_regra(palavra_chave, resposta):
    """
    Add a new response rule to the existing ruleset.
    
    Args:
        palavra_chave (str): The keyword to match in email content
        resposta (str): The response to send when the keyword is found
    """
    global REGRAS
    
    # Check if the rule already exists
    for regra in REGRAS:
        if regra["palavra_chave"].lower() == palavra_chave.lower():
            logger.warning(f"Rule for '{palavra_chave}' already exists. Updating response.")
            regra["resposta"] = resposta
            return
    
    # Add new rule
    REGRAS.append({"palavra_chave": palavra_chave, "resposta": resposta})
    logger.info(f"New rule added for keyword: '{palavra_chave}'")