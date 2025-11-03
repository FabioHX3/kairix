# 🔗 Guia de Integração com APIs Externas

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Configuração de Integrações](#configuração-de-integrações)
3. [Integração com CRM](#integração-com-crm)
4. [Integração com Gateways de Pagamento](#integração-com-gateways-de-pagamento)
5. [Integração com ERP](#integração-com-erp)
6. [Webhooks](#webhooks)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [Exemplos Práticos](#exemplos-práticos)

---

## 🎯 Visão Geral

O sistema Kairix permite integração com diversos sistemas externos através de webhooks e APIs REST. Todas as integrações são configuradas no dashboard do cliente e armazenadas de forma segura.

### Tipos de Integração Suportados

- **CRM** - Integração com sistemas de gestão de relacionamento com cliente
- **Gateway de Pagamento** - Integração com sistemas de pagamento
- **ERP** - Integração com sistemas de gestão empresarial
- **Outros** - Webhooks customizados

---

## ⚙️ Configuração de Integrações

### Endpoint de Configuração

```http
POST /api/config/{order_id}/integracoes
```

### Estrutura da Integração

```json
{
  "tipo": "crm|gateway_pagamento|erp|outro",
  "nome": "Nome da Integração",
  "webhook_url": "https://api.exemplo.com/webhook",
  "api_key": "sua-api-key-aqui",
  "documentacao": "Documentação e instruções",
  "ativo": true
}
```

### Campos

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| tipo | string | Sim | Tipo da integração |
| nome | string | Sim | Nome identificador |
| webhook_url | string | Não | URL do webhook |
| api_key | string | Não | Chave de API |
| documentacao | text | Não | Documentação adicional |
| ativo | boolean | Não | Status da integração (padrão: true) |

---

## 🎯 Integração com CRM

### Fluxo de Integração

```mermaid
sequenceDiagram
    Cliente->>WhatsApp: Envia mensagem
    WhatsApp->>Kairix Bot: Processa mensagem
    Kairix Bot->>Kairix API: Extrai dados do lead
    Kairix API->>CRM: POST /webhook com dados
    CRM-->>Kairix API: 200 OK
    Kairix API-->>Cliente: Confirma cadastro
```

### Payload Enviado ao CRM

Quando um novo lead é capturado, o Kairix envia os seguintes dados:

```json
{
  "evento": "novo_lead",
  "timestamp": "2025-10-20T10:30:00Z",
  "origem": "whatsapp",
  "lead": {
    "nome": "João Silva",
    "telefone": "+5565999999999",
    "email": "joao@email.com",
    "empresa": "Empresa LTDA",
    "mensagem": "Quero saber mais sobre o produto X",
    "utm_source": "instagram",
    "utm_campaign": "campanha_outubro"
  },
  "contexto": {
    "plano_interesse": "Professional",
    "produto": "Agente com IA",
    "interacoes_anteriores": 3
  }
}
```

### Headers Necessários

```http
POST /webhook HTTP/1.1
Host: api.crm.com
Content-Type: application/json
Authorization: Bearer {api_key}
User-Agent: Kairix-Bot/1.0
X-Kairix-Signature: {assinatura_hmac}
```

### Exemplo: RD Station

```json
{
  "tipo": "crm",
  "nome": "RD Station",
  "webhook_url": "https://api.rd.services/platform/conversions",
  "api_key": "sua-api-key-aqui",
  "documentacao": "Headers:\nAuthorization: Bearer {api_key}\nContent-Type: application/json\n\nPayload:\n{\n  \"event_type\": \"CONVERSION\",\n  \"event_family\": \"CDP\",\n  \"payload\": {\n    \"conversion_identifier\": \"lead-whatsapp\",\n    \"email\": \"email@exemplo.com\",\n    \"name\": \"Nome do Lead\",\n    \"mobile_phone\": \"+5565999999999\"\n  }\n}",
  "ativo": true
}
```

### Exemplo: HubSpot

```json
{
  "tipo": "crm",
  "nome": "HubSpot",
  "webhook_url": "https://api.hubapi.com/contacts/v1/contact/",
  "api_key": "sua-api-key-aqui",
  "documentacao": "Headers:\nAuthorization: Bearer {api_key}\nContent-Type: application/json\n\nPayload:\n{\n  \"properties\": [\n    {\"property\": \"email\", \"value\": \"email@exemplo.com\"},\n    {\"property\": \"firstname\", \"value\": \"Nome\"},\n    {\"property\": \"phone\", \"value\": \"+5565999999999\"},\n    {\"property\": \"company\", \"value\": \"Empresa LTDA\"}\n  ]\n}",
  "ativo": true
}
```

### Exemplo: Pipedrive

```json
{
  "tipo": "crm",
  "nome": "Pipedrive",
  "webhook_url": "https://{company}.pipedrive.com/api/v1/persons",
  "api_key": "sua-api-key-aqui",
  "documentacao": "Query params: ?api_token={api_key}\n\nPayload:\n{\n  \"name\": \"Nome do Lead\",\n  \"email\": [\"email@exemplo.com\"],\n  \"phone\": [{\n    \"value\": \"+5565999999999\",\n    \"primary\": true,\n    \"label\": \"work\"\n  }],\n  \"visible_to\": \"3\"\n}",
  "ativo": true
}
```

### Autenticação CRM

#### Bearer Token
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### API Key no Header
```http
X-API-Key: sua-api-key-aqui
```

#### API Key na URL
```http
https://api.exemplo.com/webhook?api_key=sua-api-key-aqui
```

#### Basic Auth
```http
Authorization: Basic base64(usuario:senha)
```

---

## 💳 Integração com Gateways de Pagamento

### Exemplo: Mercado Pago

```json
{
  "tipo": "gateway_pagamento",
  "nome": "Mercado Pago",
  "webhook_url": "https://api.mercadopago.com/v1/payments",
  "api_key": "APP_USR-xxxx",
  "documentacao": "Headers:\nAuthorization: Bearer {api_key}\nContent-Type: application/json\n\nPayload:\n{\n  \"transaction_amount\": 100.00,\n  \"description\": \"Plano Professional\",\n  \"payment_method_id\": \"pix\",\n  \"payer\": {\n    \"email\": \"cliente@email.com\",\n    \"first_name\": \"João\",\n    \"last_name\": \"Silva\"\n  }\n}",
  "ativo": true
}
```

### Exemplo: Stripe

```json
{
  "tipo": "gateway_pagamento",
  "nome": "Stripe",
  "webhook_url": "https://api.stripe.com/v1/payment_intents",
  "api_key": "sk_test_xxxx",
  "documentacao": "Headers:\nAuthorization: Bearer {api_key}\nContent-Type: application/x-www-form-urlencoded\n\nPayload (form-encoded):\namount=10000\ncurrency=brl\npayment_method_types[]=card\ndescription=Plano Professional",
  "ativo": true
}
```

### Webhook de Confirmação de Pagamento

O Kairix pode receber webhooks dos gateways de pagamento:

```http
POST /api/webhooks/payment
```

Payload esperado:
```json
{
  "event": "payment.approved",
  "payment_id": "123456789",
  "order_id": 5,
  "amount": 399.00,
  "status": "approved",
  "payment_method": "pix",
  "paid_at": "2025-10-20T10:30:00Z"
}
```

---

## 🏢 Integração com ERP

### Exemplo: Omie

```json
{
  "tipo": "erp",
  "nome": "Omie",
  "webhook_url": "https://app.omie.com.br/api/v1/geral/clientes/",
  "api_key": "xxxx",
  "documentacao": "Headers:\nContent-Type: application/json\n\nPayload:\n{\n  \"call\": \"IncluirCliente\",\n  \"app_key\": \"{api_key}\",\n  \"app_secret\": \"{secret}\",\n  \"param\": [{\n    \"nome_fantasia\": \"Cliente Exemplo\",\n    \"email\": \"email@exemplo.com\",\n    \"telefone1_numero\": \"6599999999\"\n  }]\n}",
  "ativo": true
}
```

### Exemplo: Bling

```json
{
  "tipo": "erp",
  "nome": "Bling",
  "webhook_url": "https://bling.com.br/Api/v2/contato/json/",
  "api_key": "xxxx",
  "documentacao": "Query params: ?apikey={api_key}\n\nPayload (XML):\n<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<contato>\n  <nome>Nome do Cliente</nome>\n  <email>email@exemplo.com</email>\n  <fone>6599999999</fone>\n</contato>",
  "ativo": true
}
```

---

## 🔔 Webhooks

### Recebendo Webhooks no Kairix

O Kairix expõe endpoints para receber webhooks de sistemas externos:

#### Endpoint Genérico
```http
POST /api/webhooks/generic
```

#### Webhook de Pagamento
```http
POST /api/webhooks/payment
```

#### Webhook de CRM
```http
POST /api/webhooks/crm
```

### Segurança de Webhooks

#### Validação de Assinatura HMAC

```python
import hmac
import hashlib

def validar_webhook(payload, signature, secret):
    """
    Valida assinatura HMAC do webhook
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)
```

#### Headers de Segurança

```http
X-Kairix-Signature: sha256=abc123...
X-Kairix-Timestamp: 1634567890
X-Kairix-Event: lead.created
```

---

## ⚠️ Tratamento de Erros

### Códigos de Resposta

| Código | Significado | Ação |
|--------|-------------|------|
| 200 | Sucesso | Dados processados |
| 201 | Criado | Recurso criado com sucesso |
| 400 | Bad Request | Validar payload |
| 401 | Não autorizado | Verificar API Key |
| 403 | Proibido | Verificar permissões |
| 404 | Não encontrado | Verificar URL |
| 429 | Too Many Requests | Implementar retry com backoff |
| 500 | Erro do servidor | Tentar novamente mais tarde |

### Retry Logic

```javascript
async function enviarParaCRM(dados, tentativa = 1) {
    const maxTentativas = 3;
    const delayBase = 1000; // 1 segundo

    try {
        const response = await fetch(webhook_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${api_key}`
            },
            body: JSON.stringify(dados)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        if (tentativa < maxTentativas) {
            const delay = delayBase * Math.pow(2, tentativa - 1);
            await new Promise(resolve => setTimeout(resolve, delay));
            return enviarParaCRM(dados, tentativa + 1);
        }

        throw error;
    }
}
```

### Logging de Erros

Todos os erros de integração são registrados:

```json
{
  "timestamp": "2025-10-20T10:30:00Z",
  "integracao_id": 5,
  "tipo": "crm",
  "nome": "RD Station",
  "erro": "HTTP 401 - Unauthorized",
  "tentativas": 3,
  "payload": {...}
}
```

---

## 📝 Exemplos Práticos

### Exemplo Completo: Captura de Lead via WhatsApp → RD Station

```javascript
// 1. Cliente envia mensagem no WhatsApp
const mensagem = {
    from: "+5565999999999",
    body: "Quero saber mais sobre o plano Professional"
};

// 2. Kairix processa e identifica como lead
const lead = {
    nome: "João Silva",
    telefone: "+5565999999999",
    interesse: "Plano Professional",
    origem: "whatsapp"
};

// 3. Kairix envia para RD Station
const payload = {
    event_type: "CONVERSION",
    event_family: "CDP",
    payload: {
        conversion_identifier: "lead-whatsapp-kairix",
        name: lead.nome,
        mobile_phone: lead.telefone,
        cf_interesse: lead.interesse,
        traffic_source: "whatsapp"
    }
};

fetch('https://api.rd.services/platform/conversions', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer sua-api-key',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
});

// 4. RD Station confirma recebimento
// Response: { "event_uuid": "abc-123", "status": "success" }
```

### Exemplo: Criar Pedido no ERP após Pagamento

```javascript
// 1. Webhook de pagamento aprovado
const pagamento = {
    order_id: 5,
    amount: 399.00,
    status: "approved",
    payment_method: "pix"
};

// 2. Buscar dados do pedido
const pedido = await fetch(`/api/orders/${pagamento.order_id}`);
const cliente = await fetch(`/api/clients/${pedido.cliente_id}`);

// 3. Enviar para ERP (Omie)
const payloadERP = {
    call: "IncluirPedido",
    app_key: "sua-app-key",
    app_secret: "seu-secret",
    param: [{
        codigo_cliente: cliente.id,
        data_previsao: new Date().toISOString(),
        etapa: "10",
        codigo_parcela: "001",
        qtde_parcelas: 1,
        det: [{
            ide: {
                codigo_produto: pedido.plano_id,
                descricao: pedido.plano.nome,
                quantidade: 1,
                valor_unitario: pedido.total
            }
        }]
    }]
};

fetch('https://app.omie.com.br/api/v1/produtos/pedido/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payloadERP)
});
```

---

## 🔍 Testando Integrações

### Ferramentas Recomendadas

1. **Postman** - Testes de API REST
2. **Webhook.site** - Captura e inspeção de webhooks
3. **RequestBin** - Debug de requisições HTTP
4. **ngrok** - Expor localhost para testes de webhook

### Teste Manual via cURL

```bash
# Testar envio para CRM
curl -X POST https://api.crm.com/webhook \
  -H "Authorization: Bearer sua-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste Lead",
    "email": "teste@email.com",
    "telefone": "+5565999999999"
  }'

# Testar webhook recebido
curl -X POST http://localhost:8012/api/webhooks/payment \
  -H "Content-Type: application/json" \
  -d '{
    "event": "payment.approved",
    "order_id": 5,
    "amount": 399.00
  }'
```

---

## 📞 Suporte

Para dúvidas sobre integrações:
- **Email**: dev@kairix.com.br
- **Documentação API**: http://localhost:8012/docs
- **WhatsApp**: (65) 99999-9999

---

## 📄 Changelog

- **v1.0** (2025-10-20) - Documentação inicial de integrações
