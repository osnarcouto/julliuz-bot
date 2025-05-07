# Julliuz Bot - Assistente Financeiro

Um bot do Telegram para gerenciamento financeiro pessoal com personalidade sarcástica.

## Funcionalidades

### 1. Gestão de Transações
- Registro de receitas e despesas
- Categorização automática
- Descrição detalhada
- Data e hora automática

### 2. Contas Fixas
- Cadastro de contas recorrentes
- Alertas de vencimento
- Categorização
- Gerenciamento de status

### 3. Metas Financeiras
- Definição de metas
- Acompanhamento de progresso
- Cálculo de valores diários necessários
- Notificações de conquistas

### 4. Alertas Inteligentes
- Limite de gastos por categoria
- Saldo baixo
- Vencimento de contas
- Personalização de alertas

### 5. Preferências do Usuário
- Moeda (R$, US$, €)
- Formato de data
- Idioma
- Notificações
- Modo escuro
- Preferências de gráficos

### 6. OCR de Comprovantes
- Processamento automático de comprovantes
- Extração de valor e descrição
- Categorização sugerida
- Confirmação manual

### 7. Visualização de Dados
- Gráficos de gastos por categoria
- Tendências mensais
- Análise comparativa
- Exportação de relatórios

## Comandos

### Básicos
- `/start` - Iniciar o bot
- `/help` - Ajuda e comandos disponíveis

### Transações
- `/add <tipo> <valor> <categoria> <descrição>` - Adicionar transação
- `/report` - Gerar relatório financeiro

### Contas
- `/bills` - Ver contas fixas
- `/bills add <nome> <valor> <dia_vencimento> <categoria>` - Adicionar conta
- `/bills update <id> <nome> <valor> <dia_vencimento> <categoria>` - Atualizar conta
- `/bills delete <id>` - Remover conta
- `/due` - Ver contas a vencer

### Metas
- `/goals` - Ver metas financeiras
- `/goals add <nome> <valor_alvo> <dias_prazo> [valor_atual]` - Adicionar meta
- `/goals update <id> <valor_progresso>` - Atualizar progresso
- `/goals delete <id>` - Remover meta

### Alertas
- `/alerts` - Ver alertas configurados
- `/alerts add <tipo> <valor> [categoria]` - Adicionar alerta
- `/alerts update <id> <valor>` - Atualizar alerta
- `/alerts delete <id>` - Remover alerta

### Preferências
- `/preferences` - Ver preferências
- `/preferences set <opção> <valor>` - Alterar preferência

### Comprovantes
- `/receipt` - Processar comprovante (envie uma foto)

### Gráficos
- `/charts <periodo>` - Ver gráficos de gastos
  - Períodos: week, month, year

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu_usuario/julliuz-bot.git
cd julliuz-bot
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute o bot:
```bash
python -m app.bot.main
```

## Requisitos

- Python 3.9+
- PostgreSQL
- Redis
- Tesseract OCR
- Variáveis de ambiente obrigatórias: TELEGRAM_BOT_TOKEN, DATABASE_URL, REDIS_URL

O sistema realiza checagens automáticas de dependências e variáveis obrigatórias no startup. Se algum requisito estiver ausente, a execução será interrompida com mensagem clara.

## Dependências adicionais

- [tenacity](https://tenacity.readthedocs.io/) — Usado para retries automáticos em conexões críticas (Redis, OCR, etc).

## Contribuição

Contribuições são bem-vindas! Por favor, leia o guia de contribuição antes de enviar um pull request.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 