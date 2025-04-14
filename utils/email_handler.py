"""
Email Handler Module

This module provides functionality for connecting to email servers,
reading emails, and sending responses.
"""

import imaplib
import email
import smtplib
import logging
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header

# Configure logging
logger = logging.getLogger(__name__)

class EmailHandler:
    """
    A class to handle email operations including connection,
    reading unread emails, and sending responses.
    """
    
    def __init__(self, email_usuario, email_senha, servidor_imap, servidor_smtp, porta_smtp):
        """
        Initialize the EmailHandler with connection parameters.
        
        Args:
            email_usuario (str): Email address username
            email_senha (str): Email account password
            servidor_imap (str): IMAP server address
            servidor_smtp (str): SMTP server address
            porta_smtp (int): SMTP server port
        """
        self.email_usuario = email_usuario
        self.email_senha = email_senha
        self.servidor_imap = servidor_imap
        self.servidor_smtp = servidor_smtp
        self.porta_smtp = porta_smtp
        self.imap = None
    
    def conectar_email(self):
        """
        Connect to the email server via IMAP and select the inbox.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Connect to the IMAP server
            self.imap = imaplib.IMAP4_SSL(self.servidor_imap)
            self.imap.login(self.email_usuario, self.email_senha)
            self.imap.select('INBOX')
            logger.info(f"IMAP connection established to {self.servidor_imap}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to email server: {str(e)}")
            return False
    
    def buscar_emails_nao_lidos(self):
        """
        Search for unread emails in the inbox.
        
        Returns:
            list: List of email IDs for unread messages
        """
        try:
            status, mensagens = self.imap.search(None, 'UNSEEN')
            return mensagens[0].split() if status == 'OK' else []
        except Exception as e:
            logger.error(f"Error searching for unread emails: {str(e)}")
            return []
    
    def _decode_email_header(self, header_value):
        """
        Decode email header values which might be encoded.
        
        Args:
            header_value (str): The encoded header value
            
        Returns:
            str: The decoded header value
        """
        if header_value is None:
            return ""
            
        decoded_parts = []
        parts = decode_header(header_value)
        
        for part, encoding in parts:
            if isinstance(part, bytes):
                try:
                    if encoding:
                        part = part.decode(encoding)
                    else:
                        part = part.decode('utf-8', errors='ignore')
                except:
                    part = part.decode('latin-1', errors='ignore')
            decoded_parts.append(str(part))
        
        return ' '.join(decoded_parts)
    
    def extrair_dados_email(self, num):
        """
        Fetch and extract data from a specific email.
        
        Args:
            num: The email ID to fetch
            
        Returns:
            dict: A dictionary containing email data (remetente, assunto, corpo)
        """
        try:
            status, dados = self.imap.fetch(num, '(RFC822)')
            
            if status != 'OK':
                logger.error(f"Error fetching email {num}: {status}")
                return None
            
            mensagem = email.message_from_bytes(dados[0][1])
            
            # Get and decode sender and subject
            remetente = self._decode_email_header(mensagem['From'])
            assunto = self._decode_email_header(mensagem['Subject'])
            
            # Extract the actual email address from "Name <email@example.com>" format
            match = re.search(r'<([^>]+)>', remetente)
            if match:
                remetente = match.group(1)
            
            # Extract email body (plain text preferred, HTML as fallback)
            corpo = ""
            if mensagem.is_multipart():
                for part in mensagem.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            charset = part.get_content_charset() or 'utf-8'
                            corpo = part.get_payload(decode=True).decode(charset, errors='ignore')
                            break
                        except Exception as e:
                            logger.warning(f"Error decoding plain text email part: {str(e)}")
                            continue
                    
                # If no plain text found, try HTML
                if not corpo:
                    for part in mensagem.walk():
                        content_type = part.get_content_type()
                        if content_type == "text/html":
                            try:
                                charset = part.get_content_charset() or 'utf-8'
                                html_corpo = part.get_payload(decode=True).decode(charset, errors='ignore')
                                # Simple HTML to text conversion
                                corpo = re.sub(r'<[^>]+>', ' ', html_corpo)
                                break
                            except Exception as e:
                                logger.warning(f"Error decoding HTML email part: {str(e)}")
                                continue
            else:
                # If the message is not multipart
                try:
                    charset = mensagem.get_content_charset() or 'utf-8'
                    corpo = mensagem.get_payload(decode=True).decode(charset, errors='ignore')
                except Exception as e:
                    logger.warning(f"Error decoding email body: {str(e)}")
                    corpo = mensagem.get_payload(decode=True).decode('latin-1', errors='ignore')
            
            return {
                'remetente': remetente,
                'assunto': assunto,
                'corpo': corpo
            }
            
        except Exception as e:
            logger.error(f"Error extracting email data: {str(e)}")
            return None
    
    def enviar_resposta_email(self, destinatario, assunto_original, mensagem):
        """
        Send an email response.
        
        Args:
            destinatario (str): The recipient email address
            assunto_original (str): The original email subject
            mensagem (str): The message body to send
            
        Returns:
            bool: True if send successful, False otherwise
        """
        try:
            # Create the email message
            email_msg = MIMEMultipart()
            email_msg['From'] = self.email_usuario
            email_msg['To'] = destinatario
            email_msg['Subject'] = f"Re: {assunto_original}"
            
            # Add the message body
            email_msg.attach(MIMEText(mensagem, 'plain', 'utf-8'))
            
            # Connect to SMTP server and send the message
            with smtplib.SMTP(self.servidor_smtp, self.porta_smtp) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(self.email_usuario, self.email_senha)
                smtp.send_message(email_msg)
            
            logger.info(f"Response email sent to {destinatario}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending response email: {str(e)}")
            return False
    
    def desconectar(self):
        """Close the IMAP connection if it exists."""
        try:
            if self.imap:
                self.imap.close()
                self.imap.logout()
                logger.info("IMAP connection closed")
        except Exception as e:
            logger.error(f"Error disconnecting from email server: {str(e)}")