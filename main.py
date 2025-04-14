#!/usr/bin/env python3
"""
Automated Email Response System - Main Module

This script connects to an email inbox, reads unread emails, 
and automatically responds based on predefined rules.
It can be run standalone or as part of the Flask web application.
"""

import os
import logging
import re
from dotenv import load_dotenv
from utils.email_handler import EmailHandler
from regras_email import gerar_resposta_assistente, REGRAS

# Import Flask app for use with Gunicorn
from app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def process_emails():
    """Process unread emails and send automated responses"""
    
    # Get email configuration from environment variables
    email_usuario = os.getenv("EMAIL_USUARIO")
    email_senha = os.getenv("EMAIL_SENHA")
    servidor_imap = os.getenv("SERVIDOR_IMAP", "imap.gmail.com")
    servidor_smtp = os.getenv("SERVIDOR_SMTP", "smtp.gmail.com")
    porta_smtp = int(os.getenv("PORTA_SMTP", 587))
    
    # Validate required environment variables
    if not all([email_usuario, email_senha]):
        logger.error("Missing required environment variables. Please check your .env file.")
        return
    
    try:
        # Initialize email handler
        email_handler = EmailHandler(
            email_usuario=email_usuario,
            email_senha=email_senha,
            servidor_imap=servidor_imap,
            servidor_smtp=servidor_smtp,
            porta_smtp=porta_smtp
        )
        
        # Connect to email server
        if not email_handler.conectar_email():
            logger.error("Failed to connect to email server. Please check your credentials.")
            return
            
        logger.info("Successfully connected to email server")
        
        # Fetch unread emails
        mensagens = email_handler.buscar_emails_nao_lidos()
        num_mensagens = len(mensagens)
        logger.info(f"🔍 Found {num_mensagens} unread emails")
        
        # Process each unread email
        for idx, num in enumerate(mensagens, 1):
            logger.info(f"Processing email {idx} of {num_mensagens}")
            
            try:
                # Extract email data
                email_data = email_handler.extrair_dados_email(num)
                
                if email_data:
                    remetente = email_data['remetente']
                    assunto = email_data['assunto']
                    corpo = email_data['corpo']
                    
                    # Log email information
                    logger.info(f"\n📩 New email from: {remetente}")
                    logger.info(f"Subject: {assunto}")
                    logger.info(f"Body: {corpo[:100]}...")
                    
                    # Generate response based on rules
                    resposta, matched_rule = gerar_resposta_assistente(assunto, corpo, return_matched=True)
                    logger.info(f"🤖 Generated response: {resposta[:100]}...")
                    
                    # Send response
                    success = email_handler.enviar_resposta_email(
                        destinatario=remetente,
                        assunto_original=assunto,
                        mensagem=resposta
                    )
                    
                    if success:
                        logger.info(f"📤 Response sent to {remetente}")
                    else:
                        logger.error(f"Failed to send response to {remetente}")
                    
                    # Log to database if we're running as part of the web app
                    try:
                        with app.app_context():
                            from models import EmailLog
                            from app import db
                            
                            log_entry = EmailLog(
                                sender=remetente,
                                subject=assunto,
                                matched_rule=matched_rule,
                                response_sent=success
                            )
                            db.session.add(log_entry)
                            db.session.commit()
                            logger.info(f"Email processing logged to database")
                    except Exception as e:
                        logger.error(f"Error logging to database: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error processing email {idx}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in email processing: {str(e)}")
    
    finally:
        # Cleanup and close connections
        if 'email_handler' in locals():
            try:
                email_handler.desconectar()
            except Exception as e:
                logger.error(f"Error disconnecting: {str(e)}")
            logger.info("Email connections closed")

def sync_rules_with_database():
    """Synchronize in-memory rules with database rules"""
    try:
        with app.app_context():
            from models import Rule
            
            # Get all active rules from database
            db_rules = Rule.query.filter_by(is_active=True).all()
            
            # Update in-memory rules
            global REGRAS
            REGRAS.clear()
            
            for rule in db_rules:
                REGRAS.append({
                    "palavra_chave": rule.keyword,
                    "resposta": rule.response
                })
                
            logger.info(f"Synchronized {len(REGRAS)} rules from database")
    except Exception as e:
        # We're running standalone, not as part of the web app
        logger.warning(f"Could not sync rules with database: {str(e)}")
        logger.info("Using default rules")

def main():
    """Main execution function"""
    # Try to sync rules with database
    try:
        sync_rules_with_database()
    except Exception as e:
        logger.warning(f"Could not sync rules with database: {str(e)}")
    
    # Process emails
    process_emails()

# Run as standalone script
if __name__ == "__main__":
    main()
