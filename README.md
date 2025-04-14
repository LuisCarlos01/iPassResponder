# Sistema de Auto-Resposta de Emails

Um sistema automatizado para monitoramento de emails e envio de respostas automáticas com base em regras configuráveis. Este aplicativo permite configurar palavras-chave específicas e respostas predefinidas para automatizar a comunicação via email.

![Sistema de Auto-Resposta de Emails](generated-icon.png)

## 📋 Funcionalidades

- **Monitoramento Automático:** Verifica continuamente novos emails na caixa de entrada
- **Resposta Baseada em Regras:** Envia respostas automáticas baseadas em palavras-chave detectadas
- **Interface Web Minimalista:** Dashboard intuitivo para gerenciar todo o sistema
- **Gerenciamento de Regras:** Adicionar, editar e remover regras de respostas facilmente
- **Histórico de Atividades:** Visualização de logs detalhados de todos os emails processados
- **Suporte Multi-provedor:** Compatível com Gmail, Outlook, Yahoo e outros provedores de email

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3 com Flask
- **Banco de Dados:** PostgreSQL
- **ORM:** SQLAlchemy
- **Email:** Bibliotecas imaplib2 e smtplib para manipulação de emails
- **Frontend:** HTML, CSS com Bootstrap (design minimalista)
- **Servidor:** Gunicorn para produção

## 🚀 Configuração e Instalação

### Pré-requisitos

- Python 3.8+
- PostgreSQL
- Conta de email com acesso IMAP/SMTP

### Passo a Passo para Instalação

1. **Clone o repositório:**
   ```
   git clone https://github.com/seu-usuario/sistema-auto-resposta-email.git
   cd sistema-auto-resposta-email
   ```

2. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   
   Crie um arquivo `.env` na raiz do projeto com as seguintes informações:
   ```
   # Configurações do Banco de Dados
   DATABASE_URL=postgresql://user:password@localhost:5432/auto_resposta_db
   
   # Configurações de Email
   EMAIL_USUARIO=seu_email@gmail.com
   EMAIL_SENHA=sua_senha_de_app
   SERVIDOR_IMAP=imap.gmail.com
   SERVIDOR_SMTP=smtp.gmail.com
   PORTA_SMTP=587
   ```

4. **Inicialize o banco de dados:**
   ```
   python -c "from app import db; db.create_all()"
   ```

5. **Inicie o servidor:**
   ```
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

6. **Acesse a interface web:**
   
   Abra o navegador e acesse `http://localhost:5000`

## 📝 Instruções de Uso

### Configurando o Sistema

1. **Configuração de Email:**
   - Acesse a página de "Configurações"
   - Insira seu endereço de email, senha e informações do servidor
   - Para Gmail: É necessário usar uma **Senha de App**. 
     - Ative a autenticação de dois fatores na sua conta Google
     - Acesse a seção "Senhas de App" nas configurações de segurança
     - Crie uma nova senha de aplicativo para "Email" ou "Outro"
     - Use esta senha gerada no campo "Senha" das configurações do sistema

2. **Criando Regras de Resposta:**
   - Acesse a página "Regras" e clique em "Nova Regra"
   - Digite a palavra-chave que será buscada nos emails recebidos
   - Escreva a resposta automática que será enviada quando a palavra-chave for detectada
   - Marque "Regra ativa" para habilitar imediatamente

3. **Iniciando o Monitoramento:**
   - No Dashboard, clique em "Iniciar" para começar o monitoramento automático
   - O sistema verificará novos emails a cada 5 minutos
   - Também é possível fazer uma verificação manual clicando em "Verificar Agora"

### Como Funciona

1. O sistema se conecta à sua caixa de entrada via IMAP
2. Procura emails não lidos (recebidos recentemente)
3. Analisa o assunto e corpo de cada email buscando palavras-chave configuradas
4. Quando uma correspondência é encontrada, envia a resposta associada
5. Mantém um registro detalhado de todos os emails processados
6. Se várias palavras-chave forem encontradas, usa a primeira correspondência

## 🔍 Solução de Problemas

### Problemas Comuns

- **Erro de Autenticação Gmail:** É necessário usar uma "Senha de App" específica para o Gmail, não a senha normal da conta.
- **Servidor Não Responde:** Verifique se os endereços dos servidores IMAP e SMTP estão corretos.
- **Emails Não São Detectados:** Confirme se o sistema está ativo no Dashboard.

### Verificação de Logs

Os logs detalhados do sistema podem ser acessados na interface, na seção "Logs". Eles mostram todos os emails processados e possíveis erros de processamento.

## 📊 Próximos Passos

Funcionalidades planejadas para futuras versões:

- **Análise de sentimento:** Identificação automática do tom dos emails
- **Suporte a anexos:** Envio de arquivos predefinidos nas respostas
- **Integração com CRM:** Conexão com sistemas de gestão de relacionamento
- **Interface mobile:** Versão responsiva otimizada para dispositivos móveis
- **Análise avançada de NLP:** Processamento de linguagem natural para melhor entendimento de conteúdo

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).