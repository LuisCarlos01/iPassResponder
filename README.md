# Sistema de Auto-Resposta de Emails

Sistema automatizado que responde emails baseado em regras definidas por palavras-chave.

## Funcionalidades

- Conexão automática a uma caixa de email via IMAP
- Leitura de emails não lidos e identificação de palavras-chave
- Resposta automática com base em regras pré-definidas
- Interface web para gerenciar regras e visualizar logs
- Monitoramento contínuo ou verificação manual de emails

## Configuração

### Requisitos

- Python 3.6+
- Conta de email com acesso IMAP ativado

### Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/auto-resposta-email.git
   cd auto-resposta-email
   ```

2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure o arquivo `.env` com suas credenciais de email:
   ```
   EMAIL_USUARIO=seu_email@gmail.com
   EMAIL_SENHA=sua_senha_ou_app_password
   SERVIDOR_IMAP=imap.gmail.com
   SERVIDOR_SMTP=smtp.gmail.com
   PORTA_SMTP=587
   SECRET_KEY=chave_secreta_para_flask
   SESSION_SECRET=chave_de_sessao_para_flask
   DATABASE_URL=sqlite:///email_autoresponder.db
   ```

   **Nota para usuários Gmail:** É recomendável usar uma "senha de app" em vez da sua senha normal. Veja [como criar uma senha de app](https://support.google.com/accounts/answer/185833).

### Executando o Sistema

1. Inicie a interface web:
   ```
   python wsgi.py
   ```

2. Para executar o monitoramento de email em background:
   ```
   python main.py
   ```

3. Acesse a interface web em `http://localhost:5000`

## Como Usar

### Interface Web

- **Dashboard**: Visão geral do sistema, status do monitoramento e estatísticas
- **Regras**: Adicionar, editar e remover regras de resposta
- **Logs**: Histórico de emails processados
- **Configurações**: Configurações do servidor de email

### Adicionando Regras

1. Acesse a seção "Regras" na interface web
2. Clique em "Nova Regra"
3. Defina uma palavra-chave e a resposta desejada
4. Salve a regra

### Verificação Manual de Emails

Na interface web, clique no botão "Verificar Agora" para processar os emails não lidos sem precisar iniciar o monitoramento contínuo.

## Solução de Problemas

### Erro de Autenticação

- Verifique se suas credenciais estão corretas no arquivo `.env`
- Para Gmail, certifique-se de usar uma "senha de app" e ter o IMAP ativado
- Confirme se não há restrições de segurança bloqueando o acesso

### Emails Não São Processados

- Verifique se o monitoramento está ativo
- Confirme se os emails estão marcados como "não lidos"
- Verifique os logs para possíveis erros

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.