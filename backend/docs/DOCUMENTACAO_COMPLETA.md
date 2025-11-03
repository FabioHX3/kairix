# 📚 Documentação Completa - Kairix Backend

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Instalação](#instalação)
4. [API Reference](#api-reference)
5. [Modelos de Dados](#modelos-de-dados)
6. [Fluxo de Autenticação](#fluxo-de-autenticação)
7. [Sistema de Configuração](#sistema-de-configuração)
8. [Integrações](#integrações)
9. [Sistema Financeiro](#sistema-financeiro)

---

## 🎯 Visão Geral

**Kairix** é uma plataforma de automação WhatsApp com três produtos principais:

### Produtos
1. **Agente Normal** - Bot com respostas predefinidas e menu interativo
2. **Agente com IA** - Bot inteligente com RAG e base de conhecimento
3. **Agente Financeiro** - Gestão financeira automática via WhatsApp

### Planos por Produto

#### Agente Normal
- **Starter**: R$ 199/mês - 50 respostas, menu básico
- **Professional**: R$ 399/mês - 100 respostas, múltiplos fluxos, CRM
- **Enterprise**: R$ 799/mês - Ilimitado, API, dashboard executivo

#### Agente com IA
- **IA Essencial**: R$ 499/mês - 100MB base, 1000 interações/mês
- **IA Professional**: R$ 999/mês - 500MB base, 5000 interações/mês
- **IA Enterprise**: R$ 1999/mês - Ilimitado, fine-tuning

#### Agente Financeiro
- **Básico**: R$ 299/mês - Até 500 transações/mês
- **Professional**: R$ 599/mês - Até 2000 transações/mês
- **Enterprise**: R$ 1199/mês - Ilimitado

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/JS)                    │
│  - Site Institucional                                    │
│  - Páginas de Produtos                                   │
│  - Cadastro de Clientes                                  │
│  - Login                                                 │
│  - Dashboard de Configuração                             │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼─────────────────────────────────────┐
│              BACKEND (FastAPI)                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Routers:                                        │   │
│  │  - /api/plans      - Gestão de planos           │   │
│  │  - /api/clients    - Gestão de clientes         │   │
│  │  - /api/orders     - Gestão de pedidos          │   │
│  │  - /api/auth       - Autenticação                │   │
│  │  - /api/config     - Configurações do bot        │   │
│  │  - /api/finance    - Sistema financeiro (NEW)    │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼─────────────────────────────────────┐
│              DATABASE (PostgreSQL)                       │
│  Tables:                                                 │
│  - planos          - Planos disponíveis                  │
│  - clientes        - Clientes cadastrados                │
│  - pedidos         - Pedidos realizados                  │
│  - historico_status_pedidos - Histórico de status        │
│  - transacoes_financeiras   - Transações (NEW)           │
│  - categorias_financeiras   - Categorias (NEW)           │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.9+
- PostgreSQL 12+
- pip

### Passo a Passo

```bash
# 1. Clone o repositório
cd /mnt/c/PROJETOS/kairix/backend

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais do banco

# 5. Popule o banco com planos
python populate_plans.py

# 6. Inicie o servidor
python main.py
```

### Variáveis de Ambiente (.env)

```env
# Database
DATABASE_URL=postgresql://usuario:senha@localhost/kairix_db

# Server
HOST=0.0.0.0
PORT=8012
RELOAD=True

# Security (opcional)
SECRET_KEY=sua-chave-secreta-aqui
```

---

## 📡 API Reference

### Base URL
```
http://localhost:8012
```

### Autenticação

#### POST /api/auth/login
Autentica um cliente e retorna dados do pedido mais recente.

**Request:**
```json
{
  "email": "cliente@email.com",
  "senha": "(65) 99934-2690"
}
```

**Response:**
```json
{
  "client_id": 1,
  "nome": "João Silva",
  "email": "cliente@email.com",
  "order_id": 5,
  "agent_type": "agente_normal",
  "plan_name": "Professional"
}
```

---

### Planos

#### GET /api/plans
Lista todos os planos disponíveis.

**Response:**
```json
[
  {
    "id": 1,
    "nome": "Starter",
    "tipo": "agente_normal",
    "preco": 199.00,
    "descricao": "Plano básico com respostas predefinidas",
    "recursos": {...}
  }
]
```

#### GET /api/plans/{plan_id}
Retorna detalhes de um plano específico.

---

### Clientes

#### POST /api/clients
Cadastra novo cliente.

**Request:**
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "telefone": "(65) 99999-9999",
  "whatsapp": "(65) 99999-9999",
  "empresa": "Empresa LTDA",
  "senha": "minhasenha123"
}
```

**Response:**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "criado_em": "2025-10-20T10:00:00"
}
```

#### GET /api/clients/{client_id}
Retorna dados de um cliente.

---

### Pedidos

#### POST /api/orders
Cria novo pedido.

**Request:**
```json
{
  "cliente_id": 1,
  "plano_id": 2,
  "observacoes": "Preciso de suporte para integração"
}
```

**Response:**
```json
{
  "id": 5,
  "cliente_id": 1,
  "plano_id": 2,
  "status": "aguardando_pagamento",
  "total": 399.00,
  "criado_em": "2025-10-20T10:00:00"
}
```

#### GET /api/orders/{order_id}
Retorna detalhes do pedido.

#### GET /api/orders/client/{client_id}
Lista todos os pedidos de um cliente.

#### PUT /api/orders/{order_id}
Atualiza status do pedido.

**Request:**
```json
{
  "status": "pagamento_aprovado",
  "observacoes": "Pagamento confirmado via PIX"
}
```

#### GET /api/orders/{order_id}/history
Retorna histórico de status do pedido.

---

### Configurações

#### GET /api/config/{order_id}
Retorna configuração completa do pedido.

**Response:**
```json
{
  "pedido_id": 1,
  "tipo_agente": "agente_normal",
  "configuracao": {
    "numero_whatsapp": "(65) 99934-2690",
    "respostas": [...],
    "menu": [...],
    "fluxos": [...],
    "integracoes": [...]
  },
  "configurado": true
}
```

#### PUT /api/config/{order_id}
Atualiza configuração geral.

---

### Respostas Predefinidas

#### GET /api/config/{order_id}/respostas
Lista todas as respostas.

#### POST /api/config/{order_id}/respostas
Cria nova resposta.

**Request:**
```json
{
  "pergunta": "Qual o horário de atendimento?",
  "resposta": "Atendemos de segunda a sexta, das 8h às 18h",
  "palavras_chave": ["horário", "hora", "quando", "atendimento"]
}
```

#### PUT /api/config/{order_id}/respostas/{resposta_id}
Atualiza resposta existente.

#### DELETE /api/config/{order_id}/respostas/{resposta_id}
Remove resposta.

---

### Menu Interativo

#### GET /api/config/{order_id}/menu
Lista opções do menu.

#### POST /api/config/{order_id}/menu
Cria opção de menu.

**Request:**
```json
{
  "numero": "1",
  "titulo": "Falar com Atendente",
  "descricao": "Você será transferido para um atendente humano"
}
```

#### PUT /api/config/{order_id}/menu/{menu_id}
Atualiza opção.

#### DELETE /api/config/{order_id}/menu/{menu_id}
Remove opção.

---

### Fluxos de Conversa

#### GET /api/config/{order_id}/fluxos
Lista fluxos.

#### POST /api/config/{order_id}/fluxos
Cria fluxo.

**Request:**
```json
{
  "nome": "Fluxo de Vendas",
  "descricao": "Fluxo para vendas e orçamentos",
  "etapas": [
    {
      "ordem": 1,
      "tipo": "pergunta",
      "mensagem": "Qual produto você deseja?",
      "opcoes": ["Produto A", "Produto B"]
    },
    {
      "ordem": 2,
      "tipo": "informacao",
      "mensagem": "Ótima escolha! Vou buscar as informações..."
    }
  ]
}
```

#### PUT /api/config/{order_id}/fluxos/{fluxo_id}
Atualiza fluxo.

#### DELETE /api/config/{order_id}/fluxos/{fluxo_id}
Remove fluxo.

---

### Integrações

#### GET /api/config/{order_id}/integracoes
Lista integrações.

#### POST /api/config/{order_id}/integracoes
Cria integração.

**Request:**
```json
{
  "tipo": "crm",
  "nome": "RD Station",
  "webhook_url": "https://api.rdstation.com/webhook",
  "api_key": "sua-api-key-aqui",
  "documentacao": "Headers necessários:\nAuthorization: Bearer TOKEN\nContent-Type: application/json",
  "ativo": true
}
```

#### PUT /api/config/{order_id}/integracoes/{integracao_id}
Atualiza integração.

#### DELETE /api/config/{order_id}/integracoes/{integracao_id}
Remove integração.

---

## 🗄️ Modelos de Dados

### Cliente
```python
{
  "id": Integer (PK),
  "nome": String(200),
  "email": String(200) UNIQUE,
  "telefone": String(20),
  "whatsapp": String(20),
  "empresa": String(200),
  "senha_hash": String(256),
  "criado_em": DateTime
}
```

### Plano
```python
{
  "id": Integer (PK),
  "nome": String(100),
  "tipo": Enum(agente_normal, agente_ia, agente_financeiro),
  "preco": Float,
  "descricao": Text,
  "recursos": JSON
}
```

### Pedido
```python
{
  "id": Integer (PK),
  "cliente_id": Integer (FK),
  "plano_id": Integer (FK),
  "status": Enum(cadastro_feito, aguardando_pagamento, ...),
  "total": Float,
  "configuracao_agente": JSON,
  "data_pagamento": DateTime,
  "criado_em": DateTime
}
```

---

## 🔐 Fluxo de Autenticação

```mermaid
sequenceDiagram
    Cliente->>Frontend: Acessa /login
    Frontend->>API: POST /api/auth/login
    API->>Database: Busca cliente por email
    Database-->>API: Retorna cliente
    API->>API: Valida senha (SHA-256)
    API->>Database: Busca pedido mais recente
    Database-->>API: Retorna pedido + plano
    API-->>Frontend: Retorna dados completos
    Frontend->>Frontend: Salva client_id no localStorage
    Frontend->>Dashboard: Redireciona para /configurar
```

---

## ⚙️ Sistema de Configuração

### Estrutura JSON
Todas as configurações são armazenadas em `pedidos.configuracao_agente`:

```json
{
  "numero_whatsapp": "(65) 99934-2690",
  "respostas": [
    {
      "id": 1,
      "pergunta": "Horário?",
      "resposta": "8h às 18h",
      "palavras_chave": ["horário", "hora"]
    }
  ],
  "menu": [
    {
      "id": 1,
      "numero": "1",
      "titulo": "Atendente",
      "descricao": "Falar com humano"
    }
  ],
  "fluxos": [
    {
      "id": 1,
      "nome": "Vendas",
      "descricao": "Fluxo vendas",
      "etapas": [...]
    }
  ],
  "integracoes": [
    {
      "id": 1,
      "tipo": "crm",
      "nome": "RD Station",
      "webhook_url": "https://...",
      "api_key": "...",
      "ativo": true
    }
  ]
}
```

---

## 🔗 Integrações

Ver documento separado: **[API_INTEGRATION.md](./API_INTEGRATION.md)**

---

## 💰 Sistema Financeiro

Ver documento separado: **[FINANCIAL_SYSTEM.md](./FINANCIAL_SYSTEM.md)**

---

## 📞 Suporte

- **Email**: suporte@kairix.com.br
- **WhatsApp**: (65) 99999-9999
- **Documentação**: http://localhost:8012/docs (Swagger)

---

## 📄 Licença

Copyright © 2025 Kairix - Todos os direitos reservados
