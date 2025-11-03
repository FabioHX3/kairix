# 🔌 Integração Evolution API - Kairix

## ✅ O QUE FOI IMPLEMENTADO

### 1. Router Evolution API (`routers/evolution.py`)

**Webhooks e Processamento Inteligente:**
- ✅ Endpoint webhook para receber mensagens do WhatsApp
- ✅ Processador de mensagens com busca inteligente (remove acentos, busca parcial)
- ✅ Suporte a respostas rápidas (palavras-chave)
- ✅ Suporte a menu interativo com submenus
- ✅ Sistema de fluxos de conversa (menu → resposta/submenu/atendente)
- ✅ Integração com IA (para planos Bot IA e Agente Financeiro)
- ✅ Funções para enviar mensagens de texto e botões via Evolution

**APIs de Configuração:**
- `POST /api/evolution/config/{pedido_id}` - Salvar configuração Evolution
- `GET /api/evolution/config/{pedido_id}` - Buscar configuração Evolution
- `POST /api/evolution/test/{pedido_id}` - Testar conexão Evolution
- `POST /api/evolution/send-test/{pedido_id}` - Enviar mensagem de teste
- `POST /api/evolution/webhook/{pedido_id}` - Receber webhooks do Evolution

### 2. Modelo de Dados (`models.py`)

Nova tabela `ConfiguracaoBot` com campos:
- Mensagens (boas-vindas, não entendida)
- Respostas rápidas (JSON)
- Menu interativo (JSON)
- Fluxos de conversa (JSON)
- **Credenciais Evolution** (URL, API Key, Instance Name)
- Configurações de IA (provider, modelo, embeddings)
- Horário de atendimento

### 3. Interface Web (`static/conectar-evolution.html`)

Página completa para conectar Evolution API:
- ✅ Status de conexão (conectado/desconectado)
- ✅ Formulário para URL, API Key e Instance Name
- ✅ Botão "Testar Conexão"
- ✅ Instruções passo a passo para configurar webhook
- ✅ URL do webhook gerada automaticamente
- ✅ Design Kairix (preto/vermelho)

### 4. Dependências Instaladas
- ✅ `httpx` - Cliente HTTP assíncrono para comunicação com Evolution API

---

## 🚀 COMO USAR

### Passo 1: Configurar o .env

O arquivo `.env` foi criado com variáveis de exemplo. **IMPORTANTE:** Você precisa preencher com suas credenciais reais!

```env
# ============ BANCO DE DADOS ============
# SUBSTITUA pelos dados corretos do seu PostgreSQL
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/kairix_db

# ============ EVOLUTION API ============
# URL do seu servidor Evolution (exemplo)
EVOLUTION_API_URL=http://localhost:8080

# API Key do Evolution (você pega no painel Evolution)
EVOLUTION_API_KEY=sua_api_key_aqui

# Nome da instância WhatsApp no Evolution
EVOLUTION_INSTANCE_NAME=kairix

# URL pública do Kairix (para receber webhooks)
KAIRIX_PUBLIC_URL=https://seu-dominio.com
```

### Passo 2: Instalar Dependências

```bash
source venv/bin/activate
pip install httpx
```

### Passo 3: Iniciar o Servidor

```bash
python main.py
```

### Passo 4: Conectar Evolution API

1. Acesse: `http://localhost:8012/conectar-evolution?pedido=1`
2. Preencha:
   - URL do Evolution API (ex: `http://localhost:8080`)
   - API Key (encontre no painel Evolution)
   - Nome da Instância (ex: `kairix`)
3. Clique em **"Testar Conexão"** para verificar
4. Clique em **"Salvar Configuração"**
5. Copie a URL do webhook gerada
6. Configure no painel Evolution:
   - Vá em **Configurações → Webhooks**
   - Cole a URL: `http://seu-dominio.com/api/evolution/webhook/1`
   - Ative o evento: `messages.upsert`
   - Salve

---

## 📡 COMO FUNCIONA O FLUXO

```
WhatsApp
   ↓
Evolution API
   ↓
Webhook → http://localhost:8012/api/evolution/webhook/{pedido_id}
   ↓
Kairix processa:
   - Busca respostas rápidas (palavras-chave)
   - Verifica menu interativo
   - Se tem IA, processa com IA
   - Senão, retorna resposta padrão
   ↓
Kairix envia resposta via Evolution API
   ↓
Evolution API
   ↓
WhatsApp (usuário recebe)
```

---

## 🧠 SISTEMA INTELIGENTE

### Busca por Palavras-Chave (Normalizada)

O sistema remove acentos e faz busca parcial:

```
Usuário digita: "qual horario de atendimento?"
Sistema normaliza: "qual horario de atendimento"
Palavra-chave cadastrada: "horário"
Sistema normaliza: "horario"
✅ MATCH! Retorna resposta cadastrada
```

### Menu Interativo com Fluxos

```json
{
  "numero": "1",
  "titulo": "Falar com Atendente",
  "descricao": "Você será transferido...",
  "acao": "atendente"
}
```

Ações disponíveis:
- `resposta` - Envia uma resposta de texto
- `submenu` - Abre outro menu (array de opções)
- `atendente` - Transfere para humano

### Diferença entre Planos

**Bot Normal:**
- ✅ Respostas rápidas
- ✅ Menu interativo
- ❌ SEM IA

**Bot com IA:**
- ✅ Respostas rápidas
- ✅ Menu interativo
- ✅ IA (processa mensagens não encontradas)
- ✅ Base de conhecimento vetorizada

**Agente Financeiro:**
- ✅ Tudo do Bot IA
- ✅ Contexto financeiro específico

---

## 🔧 ARQUIVOS CRIADOS/MODIFICADOS

### Novos Arquivos:
- `routers/evolution.py` - Router da integração
- `static/conectar-evolution.html` - Interface de conexão
- `.env` - Variáveis de ambiente (preencher!)
- `INTEGRACAO_EVOLUTION_API.md` - Esta documentação

### Arquivos Modificados:
- `models.py` - Adicionada tabela `ConfiguracaoBot`
- `main.py` - Importado router evolution + nova rota

---

## 📋 ENDPOINTS DA API

### Configuração

**Salvar Configuração Evolution**
```http
POST /api/evolution/config/{pedido_id}
Content-Type: application/json

{
  "evolution_url": "http://localhost:8080",
  "evolution_key": "sua_api_key",
  "evolution_instance": "kairix",
  "kairix_url": "https://seu-dominio.com"
}
```

**Buscar Configuração**
```http
GET /api/evolution/config/{pedido_id}
```

**Testar Conexão**
```http
POST /api/evolution/test/{pedido_id}
```

### Webhook

**Receber Mensagens do WhatsApp**
```http
POST /api/evolution/webhook/{pedido_id}
Content-Type: application/json

{
  "event": "messages.upsert",
  "data": {
    "key": {"remoteJid": "5565999342690@s.whatsapp.net"},
    "message": {"conversation": "oi"}
  }
}
```

---

## ⚠️ PROBLEMAS CONHECIDOS E SOLUÇÕES

### Erro: "password authentication failed for user 'user'"

**Causa:** DATABASE_URL no `.env` está com credenciais de exemplo

**Solução:** Edite o `.env` e coloque as credenciais CORRETAS do seu PostgreSQL:

```env
DATABASE_URL=postgresql://SEU_USUARIO:SUA_SENHA@localhost:5432/SEU_BANCO
```

### Erro: "No module named 'httpx'"

**Solução:**
```bash
source venv/bin/activate
pip install httpx
```

---

## 🧪 TESTANDO A INTEGRAÇÃO

### Teste 1: Conexão com Evolution

1. Abra: `http://localhost:8012/conectar-evolution?pedido=1`
2. Preencha os dados
3. Clique em "Testar Conexão"
4. Deve aparecer: ✅ "Conexão estabelecida com sucesso!"

### Teste 2: Webhook

1. Configure o webhook no Evolution
2. Envie uma mensagem para o WhatsApp conectado
3. Verifique os logs do servidor Kairix
4. O bot deve responder automaticamente

### Teste 3: Respostas Rápidas

1. Configure uma resposta rápida:
   - Palavra-chave: `["horario", "horário"]`
   - Resposta: `"Funcionamos de segunda a sexta, 9h às 18h"`
2. Envie: "qual o horário?"
3. Deve receber a resposta cadastrada

---

## 📞 PRÓXIMOS PASSOS

1. ✅ **Configurar .env** com credenciais corretas
2. ✅ **Iniciar servidor** e testar página de conexão
3. ✅ **Conectar Evolution API** via interface web
4. ✅ **Configurar webhook** no painel Evolution
5. ✅ **Testar** enviando mensagens
6. 🔜 **Implementar IA** (OpenAI/Claude) para planos IA
7. 🔜 **Implementar vetorização** de documentos
8. 🔜 **n8n** (opcional) para workflows complexos

---

## 📚 RECURSOS ADICIONAIS

- [Documentação Evolution API](https://doc.evolution-api.com/)
- [Eventos de Webhook](https://doc.evolution-api.com/v2/pt/webhooks)
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [HTTPX Client](https://www.python-httpx.org/)

---

**Criado em:** 21/10/2025
**Versão:** 1.0
**Status:** ✅ Pronto para testar (após configurar .env)
