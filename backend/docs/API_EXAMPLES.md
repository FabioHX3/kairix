# Exemplos de Uso da API Kairix

## Listar todos os planos

```bash
curl http://localhost:8012/api/plans/
```

## Buscar plano específico

```bash
curl http://localhost:8012/api/plans/1
```

## Buscar planos por tipo

```bash
# Bot Normal
curl http://localhost:8012/api/plans/type/bot_normal

# Bot com IA
curl http://localhost:8012/api/plans/type/bot_ia

# Agente Financeiro
curl http://localhost:8012/api/plans/type/agente_financeiro
```

## Registrar cliente com plano

```bash
curl -X POST http://localhost:8012/api/orders/register \
  -H "Content-Type: application/json" \
  -d '{
    "client": {
      "name": "João Silva",
      "email": "joao@example.com",
      "phone": "(65) 99999-9999",
      "whatsapp": "(65) 99999-9999",
      "company_name": "Empresa XYZ",
      "cpf_cnpj": "123.456.789-00",
      "address": "Rua Exemplo, 123",
      "city": "Cuiabá",
      "state": "MT",
      "zipcode": "78000-000"
    },
    "plan_id": 5
  }'
```

## Listar pedidos de um cliente

```bash
curl http://localhost:8012/api/orders/client/1
```

## Buscar histórico de um pedido

```bash
curl http://localhost:8012/api/orders/1/history
```

## Atualizar status do pedido

```bash
curl -X PUT http://localhost:8012/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pagamento_aprovado",
    "notes": "Pagamento confirmado via PIX"
  }'
```

## Confirmar pagamento (Webhook)

```bash
curl -X POST http://localhost:8012/api/orders/1/confirm-payment \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method": "pix",
    "transaction_id": "TXN123456789"
  }'
```

## Buscar cliente por email

```bash
curl http://localhost:8012/api/clients/email/joao@example.com
```

## Listar pedidos por status

```bash
# Aguardando pagamento
curl http://localhost:8012/api/orders/status/aguardando_pagamento

# Pagamento aprovado
curl http://localhost:8012/api/orders/status/pagamento_aprovado

# Configurando ambiente
curl http://localhost:8012/api/orders/status/configurando_ambiente
```

## Criar um novo plano

```bash
curl -X POST http://localhost:8012/api/plans/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Plano Custom",
    "type": "bot_normal",
    "period": "mensal",
    "price": 99.90,
    "price_old": 149.90,
    "description": "Plano personalizado",
    "is_featured": false,
    "is_active": true
  }'
```

## Atualizar um plano

```bash
curl -X PUT http://localhost:8012/api/plans/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 35.00,
    "is_featured": true
  }'
```

## Status Disponíveis

- `cadastro_feito` - Cadastro Realizado
- `aguardando_pagamento` - Aguardando Pagamento
- `pagamento_aprovado` - Pagamento Aprovado
- `configurando_ambiente` - Configurando Ambiente
- `instalando_agente` - Instalando Agente
- `concluido` - Concluído
- `cancelado` - Cancelado

## Tipos de Plano

- `bot_normal` - Agente Normal
- `bot_ia` - Agente com IA
- `agente_financeiro` - Agente Financeiro

## Períodos

- `mensal` - Mensal
- `semestral` - Semestral
- `anual` - Anual
