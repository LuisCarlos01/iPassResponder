"""
Automated Email Response System - Route Definitions

This module defines the routes for the email auto-responder web interface.
"""

import os
import time
import threading
import logging
import pickle
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv
from models import Rule, EmailLog
from app import db
from utils.oauth_helper import get_authorization_url, save_credentials, create_oauth_flow

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global variables to track email monitoring thread
email_thread = None
stop_thread = False

# Token storage
TOKEN_PICKLE_PATH = 'token.pickle'

def register_routes(app):
    """Register all application routes with the Flask app."""
    
    @app.route('/')
    def index():
        """Home page - display rules and email logs."""
        rules = Rule.query.order_by(Rule.created_at.desc()).limit(5).all()
        logs = EmailLog.query.order_by(EmailLog.processed_at.desc()).limit(5).all()
        
        # Check email monitoring status
        monitoring_active = email_thread is not None and email_thread.is_alive()
        
        # Check if OAuth token exists
        oauth_configured = os.path.exists(TOKEN_PICKLE_PATH)
        
        # Check if email is configured
        email_configured = all([
            os.getenv('EMAIL_USUARIO'),
            os.getenv('EMAIL_SENHA'),
            os.getenv('SERVIDOR_IMAP'),
            os.getenv('SERVIDOR_SMTP')
        ]) or oauth_configured
        
        return render_template(
            'index.html', 
            rules=rules, 
            logs=logs, 
            monitoring_active=monitoring_active,
            email_configured=email_configured,
            oauth_configured=oauth_configured
        )
    
    @app.route('/rules')
    def list_rules():
        """Display all response rules."""
        rules = Rule.query.order_by(Rule.created_at.desc()).all()
        return render_template('rules.html', rules=rules)
    
    @app.route('/rules/add', methods=['GET', 'POST'])
    def add_rule():
        """Add a new response rule."""
        if request.method == 'POST':
            keyword = request.form.get('keyword')
            response = request.form.get('response')
            is_active = True if request.form.get('is_active') else False
            
            if not keyword or not response:
                flash('Both keyword and response are required!', 'error')
                return redirect(url_for('add_rule'))
            
            # Check if rule already exists
            existing_rule = Rule.query.filter_by(keyword=keyword).first()
            if existing_rule:
                flash(f'A rule for "{keyword}" already exists!', 'error')
                return redirect(url_for('list_rules'))
            
            # Add new rule to database
            new_rule = Rule(
                keyword=keyword,
                response=response,
                is_active=is_active
            )
            db.session.add(new_rule)
            db.session.commit()
            
            # Also update the in-memory rules
            try:
                from regras_email import adicionar_regra
                adicionar_regra(keyword, response)
            except ImportError:
                logger.warning("Could not update in-memory rules")
            
            flash(f'Rule for "{keyword}" added successfully!', 'success')
            return redirect(url_for('list_rules'))
        
        return render_template('add_rule.html')
    
    @app.route('/rules/edit/<int:rule_id>', methods=['GET', 'POST'])
    def edit_rule(rule_id):
        """Edit an existing response rule."""
        rule = Rule.query.get_or_404(rule_id)
        
        if request.method == 'POST':
            rule.keyword = request.form.get('keyword')
            rule.response = request.form.get('response')
            rule.is_active = True if request.form.get('is_active') else False
            
            db.session.commit()
            
            # Update in-memory rules
            try:
                from main import sync_rules_with_database
                sync_rules_with_database()
            except ImportError:
                logger.warning("Could not update in-memory rules")
            
            flash(f'Rule for "{rule.keyword}" updated successfully!', 'success')
            return redirect(url_for('list_rules'))
        
        return render_template('edit_rule.html', rule=rule)
    
    @app.route('/rules/delete/<int:rule_id>', methods=['POST'])
    def delete_rule(rule_id):
        """Delete a response rule."""
        rule = Rule.query.get_or_404(rule_id)
        keyword = rule.keyword
        
        db.session.delete(rule)
        db.session.commit()
        
        # Update in-memory rules
        try:
            from main import sync_rules_with_database
            sync_rules_with_database()
        except ImportError:
            logger.warning("Could not update in-memory rules")
        
        flash(f'Rule for "{keyword}" deleted successfully!', 'success')
        return redirect(url_for('list_rules'))
    
    @app.route('/logs')
    def view_logs():
        """Display email processing logs."""
        logs = EmailLog.query.order_by(EmailLog.processed_at.desc()).all()
        return render_template('logs.html', logs=logs)
    
    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        """Configure email settings."""
        # Get current environment variables
        env_vars = {
            'EMAIL_USUARIO': os.getenv('EMAIL_USUARIO', ''),
            'SERVIDOR_IMAP': os.getenv('SERVIDOR_IMAP', 'imap.gmail.com'),
            'SERVIDOR_SMTP': os.getenv('SERVIDOR_SMTP', 'smtp.gmail.com'),
            'PORTA_SMTP': os.getenv('PORTA_SMTP', '587')
        }
        
        if request.method == 'POST':
            email_user = request.form.get('email_user')
            email_password = request.form.get('email_password')
            imap_server = request.form.get('imap_server')
            smtp_server = request.form.get('smtp_server')
            smtp_port = request.form.get('smtp_port')
            
            # For demo purposes - in a real app, save to a secure config file or database
            # and update environment variables
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('settings'))
        
        return render_template('settings.html', env_vars=env_vars)
    
    @app.route('/start-monitoring', methods=['POST'])
    def start_monitoring():
        """Start the email monitoring thread."""
        global email_thread, stop_thread
        
        if email_thread and email_thread.is_alive():
            flash('Email monitoring is already running!', 'info')
            return redirect(url_for('index'))
        
        stop_thread = False
        email_thread = threading.Thread(target=check_emails_periodically)
        email_thread.daemon = True
        email_thread.start()
        
        flash('Email monitoring started successfully!', 'success')
        return redirect(url_for('index'))
    
    @app.route('/stop-monitoring', methods=['POST'])
    def stop_monitoring():
        """Stop the email monitoring thread."""
        global stop_thread
        
        stop_thread = True
        flash('Email monitoring will stop after the current cycle.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/check-status', methods=['GET'])
    def check_status():
        """Check if the email monitoring thread is running."""
        global email_thread
        
        has_oauth_token = os.path.exists(TOKEN_PICKLE_PATH)
        
        status = {
            'running': email_thread is not None and email_thread.is_alive(),
            'email_configured': all([
                os.getenv('EMAIL_USUARIO'),
                os.getenv('EMAIL_SENHA'),
                os.getenv('SERVIDOR_IMAP'),
                os.getenv('SERVIDOR_SMTP')
            ]) or has_oauth_token,
            'oauth_configured': has_oauth_token
        }
        
        return jsonify(status)
    
    @app.route('/auth/gmail')
    def auth_gmail():
        """Inicia o fluxo de autenticação OAuth2 com o Gmail."""
        try:
            # Criar o fluxo de autenticação e obter a URL
            auth_url, state = get_authorization_url()
            
            # Salvar o estado na sessão
            session['oauth_state'] = state
            
            # Redirecionar para a página de autenticação do Google
            return redirect(auth_url)
        except Exception as e:
            logger.error(f"Erro ao iniciar autenticação OAuth2: {str(e)}")
            flash(f'Erro ao iniciar autenticação: {str(e)}', 'error')
            return redirect(url_for('settings'))
    
    @app.route('/auth/callback')
    def auth_callback():
        """Callback para a autenticação OAuth2."""
        try:
            # Criar um novo fluxo de autenticação
            flow = create_oauth_flow()
            
            # Processar a resposta e obter as credenciais
            flow.fetch_token(authorization_response=request.url)
            credentials = flow.credentials
            
            # Salvar as credenciais para uso futuro
            save_credentials(credentials)
            
            # Limpar o estado da sessão
            session.pop('oauth_state', None)
            
            flash('Autenticação com Gmail realizada com sucesso!', 'success')
        except Exception as e:
            logger.error(f"Erro no callback OAuth2: {str(e)}")
            flash(f'Erro na autenticação: {str(e)}', 'error')
        
        return redirect(url_for('settings'))
    
    @app.route('/manual-check', methods=['POST'])
    def manual_check():
        """Manually check for new emails once."""
        try:
            # Check if we have OAuth2 credentials
            has_oauth_token = os.path.exists(TOKEN_PICKLE_PATH)
            
            if not has_oauth_token:
                # Check traditional credentials
                email_usuario = os.getenv("EMAIL_USUARIO")
                email_senha = os.getenv("EMAIL_SENHA")
                servidor_imap = os.getenv("SERVIDOR_IMAP", "imap.gmail.com")
                servidor_smtp = os.getenv("SERVIDOR_SMTP", "smtp.gmail.com")
                porta_smtp = int(os.getenv("PORTA_SMTP", 587))
                
                if not all([email_usuario, email_senha]):
                    flash('Email credentials are not configured. Please check settings.', 'error')
                    return redirect(url_for('index'))
            
            # Process emails in a separate thread
            threading.Thread(target=process_emails_once).start()
            
            flash('Manual email check started. Results will appear in logs.', 'info')
        except Exception as e:
            logger.error(f"Error in manual check: {str(e)}")
            flash(f'Error checking emails: {str(e)}', 'error')
        
        return redirect(url_for('index'))

def process_emails_once():
    """Process emails once manually."""
    from main import process_emails
    process_emails()

def check_emails_periodically():
    """Check for new emails at regular intervals."""
    global stop_thread
    
    from main import process_emails
    
    while not stop_thread:
        try:
            process_emails()
            # Wait for 5 minutes before checking again
            for _ in range(300):  # 5 minutes * 60 seconds
                if stop_thread:
                    break
                time.sleep(1)
        except Exception as e:
            logger.error(f"Error in email checking thread: {str(e)}")
            time.sleep(60)  # Wait 1 minute before retrying if there's an error