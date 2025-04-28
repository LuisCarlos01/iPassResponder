#!/usr/bin/env python3
"""
Gerador de Segredos para o iPassResponder

Este script auxilia novos desenvolvedores a configurar o ambiente de desenvolvimento,
gerando chaves seguras para uso nos arquivos de configuração.
"""

import os
import secrets
import shutil
from datetime import datetime
from pathlib import Path

def generate_key(length=32):
    """Gera uma chave hexadecimal segura."""
    return secrets.token_hex(length)

def setup_environment():
    """Configura o ambiente inicial para desenvolvimento."""
    print("🔐 Configurando ambiente seguro para o iPassResponder...")
    
    # Criar diretórios necessários
    directories = ["data", "models", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Diretório '{directory}' verificado/criado")
    
    # Verificar e copiar arquivo .env
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("📝 Arquivo .env criado a partir do exemplo")
    
    # Verificar e copiar arquivo config.py
    if not os.path.exists("config.py") and os.path.exists("config.py.example"):
        shutil.copy("config.py.example", "config.py")
        print("📝 Arquivo config.py criado a partir do exemplo")
    
    # Gerar chaves seguras
    secret_key = generate_key()
    session_secret = generate_key()
    
    print("\n🔑 Chaves de segurança geradas:")
    print(f"\nSECRET_KEY={secret_key}")
    print(f"SESSION_SECRET={session_secret}")
    
    # Verificar se o usuário deseja atualizar o arquivo .env
    if os.path.exists(".env"):
        update_env = input("\nDeseja atualizar o arquivo .env com essas chaves? (s/n): ").lower()
        if update_env == "s":
            # Ler o arquivo .env existente
            with open(".env", "r") as f:
                env_content = f.readlines()
            
            # Atualizar as chaves
            updated = False
            with open(".env", "w") as f:
                for line in env_content:
                    if line.startswith("SECRET_KEY="):
                        f.write(f"SECRET_KEY={secret_key}\n")
                        updated = True
                    elif line.startswith("SESSION_SECRET="):
                        f.write(f"SESSION_SECRET={session_secret}\n")
                        updated = True
                    else:
                        f.write(line)
                
                # Se as chaves não existirem, adicionar ao final
                if not updated:
                    f.write(f"\n# Chaves geradas em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"SECRET_KEY={secret_key}\n")
                    f.write(f"SESSION_SECRET={session_secret}\n")
            
            print("✅ Arquivo .env atualizado com as novas chaves")
    
    print("\n✅ Ambiente configurado com sucesso!")
    print("\n⚠️ IMPORTANTE:")
    print("1. Para o Gmail, lembre-se de criar uma 'Senha de App' em vez de usar sua senha normal")
    print("2. Edite o arquivo .env para inserir suas credenciais de e-mail")
    print("3. NUNCA compartilhe ou comite arquivos com credenciais (.env, config.py, client_secret.json, etc.)")

if __name__ == "__main__":
    setup_environment() 