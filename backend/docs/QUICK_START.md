# 🚀 Quick Start - Kairix Backend

## Instalação Rápida

### Windows

```cmd
cd backend
start.bat
```

### Linux/Mac

```bash
cd backend
chmod +x start.sh
./start.sh
```

## OU Instalação Manual

```bash
cd backend

# 1. Criar ambiente virtual
python -m venv venv

# 2. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Popular banco com planos
python populate_plans.py

# 5. Iniciar servidor
python main.py
```

## 🌐 Acessos

Após iniciar o servidor:

- **API**: http://localhost:8012
- **Documentação Swagger**: http://localhost:8012/docs
- **Cadastro**: http://localhost:8012/cadastro?plan=1
- **Painel Cliente**: http://localhost:8012/painel/1

## 🎯 Teste Rápido

### 1. Verificar Planos Cadastrados

Abra seu navegador e acesse:
```
http://localhost:8012/api/plans/
```

Você verá 9 planos cadastrados (3 de cada tipo).

### 2. Fazer um Cadastro de Teste

1. Abra: http://localhost:8012/cadastro?plan=5
2. Preencha o formulário
3. Clique em "Continuar para Pagamento"
4. Anote o ID do cliente retornado

### 3. Ver Painel do Cliente

Acesse: http://localhost:8012/painel/{ID_DO_CLIENTE}

Exemplo: http://localhost:8012/painel/1

## 📊 IDs dos Planos

### Agente Normal
- Plano 1: Starter - Mensal (R$ 32/mês)
- Plano 2: Professional - Semestral (R$ 164/semestre)
- Plano 3: Enterprise - Anual (R$ 291/ano)

### Agente com IA
- Plano 4: IA Essencial - Mensal (R$ 64/mês)
- Plano 5: IA Professional - Semestral (R$ 345/semestre) ⭐
- Plano 6: IA Enterprise - Anual (R$ 614/ano)

### Agente Financeiro
- Plano 7: Básico - Mensal (R$ 147/mês)
- Plano 8: Profissional - Semestral (R$ 749/semestre) ⭐
- Plano 9: Enterprise - Anual (R$ 1.323/ano)

## 🔄 Alterar Status de um Pedido

```bash
curl -X PUT http://localhost:8012/api/orders/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pagamento_aprovado",
    "notes": "Pagamento confirmado"
  }'
```

## 📝 Próximos Passos

1. **Integrar com Gateway de Pagamento**
   - Editar `routers/orders.py`
   - Configurar webhook do gateway

2. **Adicionar Autenticação**
   - Implementar JWT
   - Proteger endpoints admin

3. **Criar Painel Admin**
   - Interface para gerenciar pedidos
   - Visualizar estatísticas

4. **Enviar Emails**
   - Confirmação de cadastro
   - Notificações de status

## 🐛 Problemas Comuns

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "Connection refused" (Banco)
Verifique se o PostgreSQL está rodando e as credenciais no `.env`

### Porta já em uso
```bash
# Altere no .env
PORT=8013
```

## 📚 Documentação

- **README.md** - Documentação completa
- **API_EXAMPLES.md** - Exemplos de uso da API
- **Swagger UI** - http://localhost:8012/docs

## 📞 Suporte

- Email: contato@kairix.com.br
- WhatsApp: (65) 99661-0840
