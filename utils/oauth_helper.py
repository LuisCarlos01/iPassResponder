"""
OAuth Helper Module

Este módulo fornece funcionalidades para autenticação OAuth2 com o Gmail,
permitindo acesso seguro às APIs do Google sem necessidade de senhas.
"""

import os
import pickle
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Escopo para acesso total ao Gmail
SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send'
]

# Caminho para armazenar o token persistente
TOKEN_PICKLE_PATH = 'token.pickle'

def get_gmail_service():
    """
    Cria e retorna um serviço autenticado da API Gmail.
    
    Returns:
        Uma instância autenticada do serviço Gmail ou None se a autenticação falhar.
    """
    creds = None
    
    # Tenta carregar credenciais existentes do arquivo pickle
    if os.path.exists(TOKEN_PICKLE_PATH):
        with open(TOKEN_PICKLE_PATH, 'rb') as token:
            creds = pickle.load(token)
    
    # Verifica se as credenciais são válidas
    if creds and creds.valid:
        return build('gmail', 'v1', credentials=creds)
    
    # Renova o token se ele expirou mas temos um refresh token
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_PICKLE_PATH, 'wb') as token:
                pickle.dump(creds, token)
            return build('gmail', 'v1', credentials=creds)
        except Exception as e:
            print(f"Erro ao renovar o token: {e}")
            return None
    
    # Se não temos credenciais válidas, retorna None
    print("Nenhuma credencial válida encontrada. Precisa fazer a autenticação primeiro.")
    return None

def create_oauth_flow():
    """
    Cria e retorna um objeto Flow para a autenticação OAuth2.
    
    Returns:
        Um objeto Flow da biblioteca google_auth_oauthlib.
    """
    # Obter a URL base do Replit
    domain = os.environ.get('REPLIT_DEV_DOMAIN', '')
    
    # Se não tiver o domínio, usar localhost para desenvolvimento local
    if not domain:
        redirect_uri = "http://localhost:8000/auth/callback"
    else:
        redirect_uri = f"https://{domain}/auth/callback"
    
    print(f"OAuth Redirect URI: {redirect_uri}")
    
    return Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

def save_credentials(credentials):
    """
    Salva as credenciais em um arquivo pickle para uso futuro.
    
    Args:
        credentials: Objeto de credenciais OAuth2 do Google.
    """
    with open(TOKEN_PICKLE_PATH, 'wb') as token:
        pickle.dump(credentials, token)
    print("Credenciais salvas com sucesso.")

def get_authorization_url():
    """
    Gera a URL para autorização OAuth2.
    
    Returns:
        A URL de autorização.
    """
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )
    return authorization_url, state