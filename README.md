# iPassResponder - Sistema de Resposta Automática de E-mail

O iPassResponder é um sistema que automatiza respostas a e-mails com base em palavras-chave identificadas no conteúdo da mensagem, usando processamento de linguagem natural (NLP) para melhorar a detecção.

## Principais Funcionalidades

- **Análise de conteúdo**: Utiliza NLTK para processar e analisar o texto dos e-mails, detectando palavras-chave com tolerância a variações
- **Respostas automáticas**: Envia respostas pré-definidas com base nas palavras-chave detectadas
- **Prevenção de duplicidade**: Rastreia e-mails já respondidos para evitar múltiplas respostas
- **Gerenciamento de regras**: Sistema flexível para adicionar/remover regras de respostas
- **Agendamento**: Verificação automática de novos e-mails em intervalos configuráveis
- **Registro de atividades**: Sistema de logs para acompanhamento de todas as operações
- **Aprendizado de máquina**: Classificação de e-mails com ML para melhorar a precisão (opcional)

## Estrutura do Projeto

```
iPassResponder/
│
├── utils/                     # Módulos utilitários
│   ├── email_handler.py       # Manipulação de e-mail (conexão, leitura, resposta)
│   ├── text_analyzer.py       # Análise de texto com NLTK
│   ├── rule_manager.py        # Gerenciamento de regras de resposta
│   ├── scheduler.py           # Agendamento de verificações
│   └── ml_classifier.py       # Classificação com machine learning (opcional)
│
├── data/                      # Diretório para dados persistentes
│   ├── rules.json             # Regras de resposta em formato JSON
│   └── responded_emails.pickle # Registro de e-mails respondidos
│
├── models/                    # Modelos de ML treinados
│   └── email_classifier.pkl   # Modelo de classificação de e-mails
│
├── logs/                      # Arquivos de log
│
├── app.py                     # Aplicação web Flask
├── config.py                  # Configurações centralizadas
├── main.py                    # Script principal
├── models.py                  # Modelos de banco de dados SQLAlchemy
├── requirements.txt           # Dependências do projeto
├── .env                       # Variáveis de ambiente (não versionado)
└── .env.example               # Exemplo de configuração de variáveis de ambiente
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/iPassResponder.git
cd iPassResponder
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Baixe os recursos do NLTK necessários:
```bash
python -c "import nltk; nltk.download(['punkt', 'stopwords', 'rslp'])"
```

5. Configure o arquivo .env com suas credenciais:
```bash
cp .env.example .env
# Edite o arquivo .env com suas informações
```

6. Configure os arquivos de segurança:
```bash
cp config.py.example config.py
# Edite o arquivo config.py para substituir os valores padrão por valores seguros
```

## Segurança e Boas Práticas

Este projeto contém um arquivo `.gitignore` configurado para proteger informações sensíveis. Preste atenção especial aos seguintes pontos:

### Arquivos Sensíveis

Os seguintes arquivos contêm informações sensíveis e **NÃO** devem ser versionados:

- `.env` - Contém variáveis de ambiente e credenciais
- `config.py` - Contém configurações com possíveis valores sensíveis
- `client_secret.json` - Credenciais de autenticação Google
- `token.pickle` - Tokens de acesso persistentes
- `*.key`, `*.pem` - Chaves privadas e certificados
- Banco de dados em `instance/` - Contém dados do sistema

### Setup Inicial para Novos Desenvolvedores

1. Copie os arquivos de exemplo:
   ```bash
   cp .env.example .env
   cp config.py.example config.py
   ```

2. Gere novas chaves secretas para o Flask:
   ```bash
   python -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"
   python -c "import secrets; print(f'SESSION_SECRET={secrets.token_hex(32)}')"
   ```
   Adicione estas chaves ao seu arquivo `.env`

3. Para Gmail, crie uma senha de aplicativo:
   - Ative a autenticação de dois fatores em sua conta Google
   - Acesse a seção "Senhas de App" nas configurações de segurança
   - Crie uma nova senha para "Email" ou "Outro"
   - Use essa senha no arquivo `.env`

4. Nunca commit arquivos sensíveis:
   ```bash
   git add .
   git status   # Verifique se arquivos sensíveis não estão sendo versionados
   ```

5. Crie os diretórios necessários:
   ```bash
   mkdir -p data models logs
   ```

## Uso

### Como Script Independente

Para executar uma verificação única:
```bash
python main.py
```

Para executar com agendamento automático:
```bash
python main.py --schedule --interval 5
```

### Com Machine Learning

Para treinar o modelo de ML:
```bash
python main.py --train
```

Para usar o modelo de ML na classificação:
```bash
python main.py --ml
```

### Como Aplicação Web

Para iniciar a aplicação web:
```bash
python run.py
```

Ou com Gunicorn:
```bash
gunicorn -w 4 wsgi:app
```

## Configuração

O sistema pode ser configurado através do arquivo `.env`. As principais configurações incluem:

- `EMAIL_USUARIO`: Endereço de e-mail para conectar
- `EMAIL_SENHA`: Senha ou senha de aplicativo para o e-mail
- `SERVIDOR_IMAP`: Servidor IMAP (padrão: imap.gmail.com)
- `SERVIDOR_SMTP`: Servidor SMTP (padrão: smtp.gmail.com)
- `PORTA_SMTP`: Porta SMTP (padrão: 587)
- `CHECK_INTERVAL`: Intervalo entre verificações em minutos (padrão: 5)
- `USE_ML_MODEL`: Usar modelo de ML para classificação (true/false)
- `MIN_SIMILARITY_SCORE`: Limiar de similaridade para correspondência (0.0-1.0)

## Adicionando Novas Regras

As regras podem ser adicionadas de três maneiras:

1. **Via Banco de Dados**: Através da interface web
2. **Via Arquivo JSON**: Editando o arquivo `data/rules.json`
3. **Programaticamente**: Usando a classe `RuleManager`

Exemplo de arquivo de regras:
```json
[
  {
    "palavra_chave": "orçamento",
    "resposta": "Obrigado por solicitar um orçamento. Para podermos atendê-lo melhor, precisamos das seguintes informações..."
  },
  {
    "palavra_chave": "suporte",
    "resposta": "Recebemos sua solicitação de suporte técnico. Um de nossos especialistas irá analisar seu caso em breve..."
  }
]
```

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## Licença

Este projeto está licenciado sob a licença MIT.