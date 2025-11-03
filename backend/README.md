# Kairix - Sistema de Gestão de Vendas

Sistema completo para gestão de vendas e controle das soluções Kairix com FastAPI e PostgreSQL.

## 🚀 Funcionalidades

- **Gestão de Planos**: Cadastro e gerenciamento de planos (Bot Normal, Bot IA, Agente Financeiro)
- **Cadastro de Clientes**: Formulário completo de cadastro
- **Gestão de Pedidos**: Controle completo de pedidos com vínculo cliente-plano
- **Acompanhamento de Status**: Sistema de etapas para o cliente acompanhar o progresso
- **Painel do Cliente**: Interface para visualização de pedidos e status
- **API RESTful**: Endpoints completos para todas as operações
- **Integração com Gateway**: Pronto para integração com gateways de pagamento

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL
- pip

## 🔧 Instalação

### 1. Clone o repositório

```bash
cd backend
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o arquivo .env

O arquivo `.env` já está configurado na raiz do projeto com:

```env
DATABASE_URL=postgresql://postgres:pos22mewebmdz@192.168.0.134:5432/kairix
HOST=0.0.0.0
PORT=8012
SECRET_KEY=mdz@2025
```

### 5. Popule o banco com os planos iniciais

```bash
python populate_plans.py
```

Este comando irá criar 9 planos no banco:
- 3 planos para Bot Normal (Mensal, Semestral, Anual)
- 3 planos para Bot com IA (Mensal, Semestral, Anual)
- 3 planos para Agente Financeiro (Mensal, Semestral, Anual)

### 6. Inicie o servidor

```bash
python main.py
```

Ou com uvicorn diretamente:

```bash
uvicorn main:app --host 0.0.0.0 --port 8012 --reload
```

O servidor estará rodando em: http://localhost:8012

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8012/docs
- **ReDoc**: http://localhost:8012/redoc

## 🎯 Endpoints Principais

### Plans (Planos)

- `GET /api/plans/` - Lista todos os planos
- `GET /api/plans/{id}` - Busca um plano específico
- `GET /api/plans/type/{type}` - Busca planos por tipo
- `POST /api/plans/` - Cria um novo plano
- `PUT /api/plans/{id}` - Atualiza um plano
- `DELETE /api/plans/{id}` - Deleta um plano

### Clients (Clientes)

- `GET /api/clients/` - Lista todos os clientes
- `GET /api/clients/{id}` - Busca um cliente específico
- `GET /api/clients/email/{email}` - Busca cliente por email
- `POST /api/clients/` - Cria um novo cliente
- `PUT /api/clients/{id}` - Atualiza dados do cliente

### Orders (Pedidos)

- `GET /api/orders/` - Lista todos os pedidos
- `GET /api/orders/{id}` - Busca um pedido específico
- `GET /api/orders/client/{client_id}` - Lista pedidos de um cliente
- `GET /api/orders/status/{status}` - Lista pedidos por status
- `GET /api/orders/{id}/history` - Histórico de status do pedido
- `POST /api/orders/register` - Registra cliente com plano (usado no formulário)
- `PUT /api/orders/{id}/status` - Atualiza status do pedido
- `POST /api/orders/{id}/confirm-payment` - Confirma pagamento (webhook)

## 🌐 Páginas Web

### Formulário de Cadastro

URL: `http://localhost:8012/cadastro?plan={id}`

Exemplo: `http://localhost:8012/cadastro?plan=5`

### Painel do Cliente

URL: `http://localhost:8012/painel/{client_id}`

Exemplo: `http://localhost:8012/painel/1`

## 📊 Status dos Pedidos

O sistema trabalha com os seguintes status:

1. **cadastro_feito** - Cadastro Realizado
2. **aguardando_pagamento** - Aguardando Pagamento
3. **pagamento_aprovado** - Pagamento Aprovado
4. **configurando_ambiente** - Configurando Ambiente
5. **instalando_agente** - Instalando Agente
6. **concluido** - Concluído
7. **cancelado** - Cancelado

## 🔄 Fluxo de Compra

1. Cliente clica em "Começar Agora" em um dos planos do site
2. É redirecionado para `/cadastro?plan={id}`
3. Preenche o formulário de cadastro
4. Sistema cria o cliente e o pedido
5. Gera link de pagamento
6. Redireciona para o gateway de pagamento
7. Após confirmação do pagamento (webhook), atualiza status
8. Cliente pode acompanhar no painel: `/painel/{client_id}`

## 🔐 Segurança

- Validação de dados com Pydantic
- Criptografia de senhas (quando implementado login)
- CORS configurado
- Validação de emails únicos

## 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para Python
- **PostgreSQL** - Banco de dados relacional
- **Pydantic** - Validação de dados
- **Uvicorn** - Servidor ASGI

## 📝 Estrutura do Banco de Dados

### Tabelas

- **plans** - Planos disponíveis
- **clients** - Clientes cadastrados
- **orders** - Pedidos realizados
- **order_status_history** - Histórico de mudanças de status

## 🎨 Customização

### Alterar URL do Gateway de Pagamento

Edite o arquivo `routers/orders.py`:

```python
PAYMENT_GATEWAY_URL = "https://pay.kiwify.com.br"
```

### Adicionar Novos Status

Edite o arquivo `models.py`:

```python
class OrderStatus(str, enum.Enum):
    # Adicione novos status aqui
    MEU_STATUS = "meu_status"
```

## 🐛 Troubleshooting

### Erro de conexão com o banco

Verifique se o PostgreSQL está rodando e as credenciais no `.env` estão corretas.

### Porta já em uso

Altere a porta no arquivo `.env` ou use:

```bash
uvicorn main:app --port 8013
```

### Tabelas não criadas

Execute:

```bash
python populate_plans.py
```

Isso criará automaticamente todas as tabelas.

## 📞 Suporte

Para dúvidas ou problemas, entre em contato:
- Email: contato@kairix.com.br
- WhatsApp: (65) 99661-0840

## 📄 Licença

© 2025 Kairix. Todos os direitos reservados.
