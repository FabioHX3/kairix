# 🤖 Sistema de Agente IA com RAG

## 📋 Visão Geral

Sistema completo de **Agente Inteligente com RAG (Retrieval-Augmented Generation)** integrado ao Kairix. O agente responde perguntas dos clientes via WhatsApp usando uma base de conhecimento vetorizada.

## 🎯 Funcionalidades

### 1. **Processamento Inteligente de Mensagens**
- ✅ Aceita mensagens de **texto** e **áudio**
- ✅ Transcreve áudios automaticamente (Whisper)
- ✅ Busca informações relevantes na base de conhecimento (RAG)
- ✅ Responde em **texto + áudio** (TTS)
- ✅ Sempre inclui opção de transferência para atendente humano

### 2. **Gestão de Base de Conhecimento**
- ✅ Upload de documentos (PDF, DOCX, TXT)
- ✅ Vetorização automática com embeddings (Ollama)
- ✅ Armazenamento em Qdrant
- ✅ Listagem e exclusão de documentos
- ✅ Teste de perguntas na interface

### 3. **Transferência para Atendente**
- ✅ Detecção automática de palavras-chave
- ✅ Notificação para números de atendentes configurados
- ✅ Mesma mecânica do Agente Normal

## 🏗️ Arquitetura

```
WhatsApp (Evolution API)
    ↓
Webhook (/api/evolution/webhook/{pedido_id})
    ↓
Detecta Tipo de Agente (Plano.tipo)
    ↓
┌─────────────────────────────────────────┐
│ Agente IA (TipoAgente.IA)               │
│   ↓                                     │
│ IAHandler.handle_message()              │
│   ↓                                     │
│ ┌───────────────┬──────────────────┐    │
│ │ Texto         │ Áudio            │    │
│ └───────┬───────┴──────┬───────────┘    │
│         │              │                 │
│         │              ↓                 │
│         │         AudioService           │
│         │         (Transcrição)          │
│         │              │                 │
│         └──────────────┴─────────┐       │
│                                  ↓       │
│                          RAGService      │
│                          (Busca + LLM)   │
│                                  ↓       │
│                     ┌────────────┴────┐  │
│                     │ Texto  │ Áudio  │  │
│                     └────────┬────────┘  │
└──────────────────────────────┼───────────┘
                               ↓
                          WhatsApp
```

## 📁 Estrutura de Arquivos

```
backend/
├── rag_service.py              # Serviço de RAG (vetorização + busca)
├── audio_service.py            # Transcrição e TTS
├── ia_handler.py               # Handler de mensagens IA
├── routers/
│   └── knowledge.py            # Endpoints de gestão de documentos
├── static/
│   └── base-conhecimento.html  # Interface de upload
└── storage/
    ├── knowledge_base/         # Documentos por número
    │   └── {numero}/
    │       ├── documento1.pdf
    │       └── documento2.txt
    └── audio_cache/            # Cache de áudios TTS
        └── {numero}/
            └── response_*.mp3
```

## 🔧 Configuração

### 1. **Configurações do Sistema**

As configurações são gerenciadas pelo painel administrativo e armazenadas no banco de dados.
Não é necessário configurar variáveis de ambiente manualmente.

Acesse o painel admin em: `http://localhost:8012/admin` e configure:

- **Evolution API**: URL e API Key do servidor Evolution
- **Qdrant**: URL do servidor Qdrant (banco de vetores)
- **Ollama**: URL do servidor Ollama, modelo LLM e modelo de embeddings

As configurações são lidas automaticamente pelo sistema através do banco de dados.

### 2. **Dependências Instaladas**

```
langchain==0.1.0
langchain-community==0.0.10
qdrant-client==1.7.0
openai-whisper==20231117
pydub==0.25.1
gTTS==2.5.0
pypdf==3.17.4
python-docx==1.1.0
chardet==5.2.0
```

## 🚀 Como Usar

### 1. **Cliente com Plano Agente IA**

1. Faça login no painel do cliente: `/cliente/login`
2. No painel, clique no botão **"Gerenciar Base de Conhecimento"** (aparece apenas para planos de Agente IA)
3. Faça upload dos documentos (PDF, DOCX, TXT)
4. Aguarde a vetorização (pode demorar alguns minutos)
5. Teste perguntas na interface
6. Configure o WhatsApp normalmente no painel principal

### 2. **Fluxo de Atendimento**

**Cliente envia mensagem de texto:**
```
Cliente: "Qual o horário de funcionamento?"
  ↓
RAG busca na base de conhecimento
  ↓
LLM gera resposta contextualizada
  ↓
Bot responde em TEXTO + ÁUDIO
"Nosso horário é de segunda a sexta, das 9h às 18h.

_Para falar com um atendente humano, digite *atendente*._"
```

**Cliente envia áudio:**
```
Cliente: 🎤 "Qual o horário de funcionamento?"
  ↓
Whisper transcreve o áudio
  ↓
RAG + LLM processam
  ↓
Bot responde:
"🎙️ *Você disse:* Qual o horário de funcionamento?

Nosso horário é de segunda a sexta, das 9h às 18h.

_Para falar com um atendente humano, digite *atendente*._"
  ↓
Bot envia áudio com a resposta
```

**Cliente pede atendente:**
```
Cliente: "atendente" ou "falar com humano"
  ↓
Sistema detecta palavras-chave
  ↓
Transfere para atendentes configurados
  ↓
Atendentes recebem notificação no WhatsApp
```

## 📡 Endpoints da API

### Upload de Documento
```http
POST /api/knowledge/upload/{pedido_id}
Content-Type: multipart/form-data

file: arquivo.pdf
```

### Listar Documentos
```http
GET /api/knowledge/list/{pedido_id}

Response:
{
  "documents": [
    {
      "filename": "manual.pdf",
      "size": 1024000,
      "uploaded_at": 1234567890
    }
  ],
  "total": 1,
  "vectorized": ["manual.pdf"]
}
```

### Deletar Documento
```http
DELETE /api/knowledge/delete/{pedido_id}/{filename}
```

### Limpar Base Completa
```http
DELETE /api/knowledge/clear/{pedido_id}
```

### Testar RAG
```http
POST /api/knowledge/test/{pedido_id}?question=Como funciona?

Response:
{
  "success": true,
  "question": "Como funciona?",
  "answer": "Funciona da seguinte forma..."
}
```

## 🔄 Webhook do Evolution

O webhook detecta automaticamente o tipo de agente:

```python
# routers/evolution.py - linha 631

if pedido.plano.tipo == models.TipoAgente.IA:
    # Usa IAHandler (RAG + Áudio)
    ia_handler = IAHandler()
    await ia_handler.handle_message(...)
else:
    # Usa Agente Normal (respostas predefinidas)
    response_text = await process_message(...)
```

## 🎨 Interface de Gerenciamento

Acessível através do painel do cliente (botão "Gerenciar Base de Conhecimento")

**Funcionalidades:**
- 📤 Upload por clique ou drag & drop
- 📚 Visualização de documentos cadastrados
- 🗑️ Exclusão de documentos
- 🧪 Teste de perguntas em tempo real

## 🔐 Segurança

- ✅ Autenticação por `pedido_id`
- ✅ Validação de formato de arquivos
- ✅ Limite de tamanho (10MB)
- ✅ Isolamento de dados por número de telefone
- ✅ Coleções separadas no Qdrant por cliente

## 📊 Armazenamento

### Documentos Físicos
```
storage/knowledge_base/{numero_limpo}/
  - documento1.pdf
  - documento2.docx
  - documento3.txt
```

### Vetores (Qdrant)
```
Coleção: kb_{numero_limpo}
Vetores: embeddings de 384 dimensões
Metadados: {text, file_name, chunk_index, pedido_id}
```

### Cache de Áudios
```
storage/audio_cache/{numero_limpo}/
  - response_{hash}.mp3
```

## 🐛 Troubleshooting

### Erro: "Whisper muito lento"
- Whisper usa modelo "base" por padrão
- Modelos disponíveis: tiny, base, small, medium, large
- Trocar em `audio_service.py` linha 17

### Áudios não sendo gerados
- Verificar conexão com internet (gTTS usa API do Google)
- Verificar permissões da pasta `storage/audio_cache`

### Verificar Configurações
- Acesse o painel admin: `http://localhost:8012/admin`
- Vá em "Configurações do Sistema"
- Teste a conexão com Evolution API, Qdrant e Ollama usando os botões de teste

## 📈 Performance

- **Upload**: ~1-5 min para vetorizar 100 páginas
- **Resposta**: ~5-10 segundos (RAG + LLM + TTS)
- **Transcrição**: ~2-5 segundos para 30s de áudio
- **Cache**: Áudios idênticos são reutilizados

## 🎯 Próximas Melhorias

- [ ] Suporte a mais formatos (Excel, PowerPoint)
- [ ] Resumo automático de documentos longos
- [ ] Múltiplos idiomas
- [ ] Métricas de uso (perguntas mais frequentes)
- [ ] Fine-tuning do LLM com histórico
- [ ] Integração com outras plataformas (Telegram, Instagram)

## ✅ Status do Sistema

🟢 **SISTEMA COMPLETO E FUNCIONAL**

Todos os componentes foram criados e integrados:
- ✅ RAG Service
- ✅ Audio Service
- ✅ IA Handler
- ✅ Knowledge Router
- ✅ Webhook Integration
- ✅ Interface Web
- ✅ Documentação

**Pronto para uso!**
