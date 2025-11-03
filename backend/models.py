from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class TipoPlano(str, enum.Enum):
    AGENTE_NORMAL = "agente_normal"
    AGENTE_IA = "agente_ia"
    AGENTE_FINANCEIRO = "agente_financeiro"


class PeriodoPlano(str, enum.Enum):
    MENSAL = "mensal"
    SEMESTRAL = "semestral"
    ANUAL = "anual"


class StatusPedido(str, enum.Enum):
    CADASTRO_FEITO = "cadastro_feito"
    AGUARDANDO_PAGAMENTO = "aguardando_pagamento"
    PAGAMENTO_APROVADO = "pagamento_aprovado"
    CONFIGURANDO_AMBIENTE = "configurando_ambiente"
    INSTALANDO_AGENTE = "instalando_agente"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class Plano(Base):
    __tablename__ = "planos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(Enum(TipoPlano), nullable=False)
    periodo = Column(Enum(PeriodoPlano), nullable=False)
    preco = Column(Float, nullable=False)
    preco_antigo = Column(Float, nullable=True)
    descricao = Column(Text, nullable=True)
    recursos = Column(Text, nullable=True)  # JSON string
    link_pagamento = Column(String(500), nullable=True)  # Link do gateway de pagamento (Kirvano)
    destaque = Column(Boolean, default=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    pedidos = relationship("Pedido", back_populates="plano")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    telefone = Column(String(20), nullable=False)
    nome_empresa = Column(String(200), nullable=True)
    cpf_cnpj = Column(String(20), nullable=True)
    endereco = Column(Text, nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)
    cep = Column(String(10), nullable=True)
    whatsapp = Column(String(20), nullable=False)
    senha_hash = Column(String(200), nullable=False)  # Hash da senha para segurança
    ativo = Column(Boolean, default=False)  # Inicia desativado, ativa após pagamento
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    pedidos = relationship("Pedido", back_populates="cliente")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    plano_id = Column(Integer, ForeignKey("planos.id"), nullable=False)

    status = Column(Enum(StatusPedido), default=StatusPedido.CADASTRO_FEITO, nullable=False)
    metodo_pagamento = Column(String(50), nullable=True)
    gateway_id = Column(String(200), nullable=True)  # ID do pagamento no gateway
    link_pagamento = Column(String(500), nullable=True)
    data_pagamento = Column(DateTime, nullable=True)

    valor = Column(Float, nullable=False)
    desconto = Column(Float, default=0)
    total = Column(Float, nullable=False)

    observacoes = Column(Text, nullable=True)
    configuracao_agente = Column(Text, nullable=True)  # JSON com configurações do agente
    data_inicio = Column(Date, nullable=True)  # Data de início do plano (data do pagamento)
    data_validade = Column(Date, nullable=True)  # Data de vencimento do plano

    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    cliente = relationship("Cliente", back_populates="pedidos")
    plano = relationship("Plano", back_populates="pedidos")

# ============= CONFIGURAÇÃO DO BOT =============

class ConfiguracaoBot(Base):
    __tablename__ = "configuracoes_bot"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False, unique=True)

    # Mensagens
    mensagem_boas_vindas = Column(Text, nullable=True)
    mensagem_nao_entendida = Column(Text, nullable=True)

    # Respostas rápidas (JSON array)
    # Formato: [{"palavras_chave": ["horario", "hora"], "resposta": "Funcionamos de segunda a sexta..."}]
    respostas_rapidas = Column(Text, nullable=True)

    # Menu interativo (JSON array)
    # Formato: [{"numero": "1", "titulo": "Falar com Atendente", "descricao": "...", "acao": "atendente"}]
    menu_interativo = Column(Text, nullable=True)

    # Fluxos de conversa (JSON para fluxos complexos)
    # Formato: [{"id": 1, "tipo": "menu", "opcoes": [...], "acao_resposta": {...}}]
    fluxos_conversa = Column(Text, nullable=True)

    # Configurações Evolution API
    evolution_url = Column(String(500), nullable=True)  # URL do Evolution API
    evolution_key = Column(String(500), nullable=True)  # API Key do Evolution
    evolution_instance = Column(String(200), nullable=True)  # Nome da instância
    evolution_webhook_events = Column(String(500), nullable=True)  # Eventos do webhook (JSON array)

    # Base de conhecimento (para planos com IA)
    base_conhecimento = Column(Text, nullable=True)  # JSON array de documentos vetorizados
    embeddings_modelo = Column(String(100), nullable=True)  # Modelo usado para embeddings
    llm_provider = Column(String(50), nullable=True)  # openai, anthropic, local
    llm_model = Column(String(100), nullable=True)  # gpt-4, claude-3, etc

    # Configurações avançadas
    timeout_inatividade = Column(Integer, default=300)  # segundos
    horario_atendimento = Column(Text, nullable=True)  # JSON com horários
    mensagem_fora_horario = Column(Text, nullable=True)

    # Atendentes (JSON array de números)
    # Formato: ["5565999342609", "5565988887777"]
    numeros_atendentes = Column(Text, nullable=True)

    # Metadados
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= SISTEMA DE CONVERSAS =============

class StatusConversa(str, enum.Enum):
    ATIVA = "ativa"
    FINALIZADA = "finalizada"
    AGUARDANDO = "aguardando"
    ABANDONADA = "abandonada"


class TipoMensagem(str, enum.Enum):
    TEXTO = "texto"
    AUDIO = "audio"
    IMAGEM = "imagem"
    VIDEO = "video"
    DOCUMENTO = "documento"
    STICKER = "sticker"
    LOCALIZACAO = "localizacao"
    CONTATO = "contato"
    OUTRO = "outro"


class DirecaoMensagem(str, enum.Enum):
    RECEBIDA = "recebida"
    ENVIADA = "enviada"


class Conversa(Base):
    __tablename__ = "conversas"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)

    # Dados do contato
    contato_nome = Column(String(200), nullable=False)
    contato_numero = Column(String(20), nullable=False, index=True)
    contato_foto_url = Column(String(500), nullable=True)

    # Status e contexto
    status = Column(Enum(StatusConversa), default=StatusConversa.ATIVA, nullable=False)
    contexto = Column(Text, nullable=True)  # JSON com contexto da conversa
    tags = Column(String(500), nullable=True)  # JSON array de tags

    # Métricas da conversa
    total_mensagens = Column(Integer, default=0)
    mensagens_bot = Column(Integer, default=0)
    mensagens_usuario = Column(Integer, default=0)
    tempo_primeira_resposta = Column(Float, nullable=True)  # segundos
    tempo_resposta_medio = Column(Float, nullable=True)  # segundos

    # Dados Evolution API
    evolution_remote_jid = Column(String(200), nullable=True)  # ID do chat no Evolution
    evolution_instance = Column(String(200), nullable=True)

    # Timestamps
    iniciada_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    finalizada_em = Column(DateTime, nullable=True)
    ultima_interacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    mensagens = relationship("Mensagem", back_populates="conversa", cascade="all, delete-orphan")


class Mensagem(Base):
    __tablename__ = "mensagens"

    id = Column(Integer, primary_key=True, index=True)
    conversa_id = Column(Integer, ForeignKey("conversas.id"), nullable=False)

    # Tipo e direção
    tipo = Column(Enum(TipoMensagem), default=TipoMensagem.TEXTO, nullable=False)
    direcao = Column(Enum(DirecaoMensagem), nullable=False)

    # Conteúdo
    conteudo = Column(Text, nullable=True)  # Texto da mensagem
    midia_url = Column(String(500), nullable=True)  # URL de mídia (imagem, áudio, etc)
    midia_mimetype = Column(String(100), nullable=True)
    midia_tamanho = Column(Integer, nullable=True)  # bytes

    # Metadados
    respondida_por_bot = Column(Boolean, default=False)
    tempo_resposta = Column(Float, nullable=True)  # segundos até responder
    lida = Column(Boolean, default=False)
    erro = Column(Text, nullable=True)  # Se houve erro ao enviar/processar

    # Dados Evolution API
    evolution_message_id = Column(String(200), nullable=True, unique=True, index=True)
    evolution_key_id = Column(String(200), nullable=True)
    evolution_push_name = Column(String(200), nullable=True)  # Nome do remetente

    # Dados adicionais (JSON)
    dados_extras = Column(Text, nullable=True)  # Qualquer outro dado relevante

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    conversa = relationship("Conversa", back_populates="mensagens")


class MetricaDiaria(Base):
    __tablename__ = "metricas_diarias"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    data = Column(Date, nullable=False)

    # Métricas de conversas
    total_mensagens = Column(Integer, default=0)
    total_contatos = Column(Integer, default=0)
    conversas_iniciadas = Column(Integer, default=0)
    conversas_finalizadas = Column(Integer, default=0)

    # Métricas de desempenho
    tempo_resposta_medio = Column(Float, default=0.0)  # em segundos
    taxa_conversao = Column(Float, default=0.0)  # percentual

    # Metadados
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= ADMINISTRADORES =============

class Administrador(Base):
    __tablename__ = "administradores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    senha_hash = Column(String(200), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============= CONFIGURAÇÕES DO SISTEMA =============

class ConfiguracaoSistema(Base):
    __tablename__ = "configuracoes_sistema"

    id = Column(Integer, primary_key=True, index=True)

    # Evolution API (configurações globais)
    evolution_api_url = Column(String(500), nullable=True)
    evolution_api_key = Column(String(500), nullable=True)
    kairix_public_url = Column(String(500), nullable=True)

    # Qdrant (Base de Conhecimento Vetorizada)
    qdrant_url = Column(String(500), nullable=True)
    qdrant_api_key = Column(String(500), nullable=True)
    qdrant_collection = Column(String(200), nullable=True)

    # Ollama (IA Local) - único provider usado
    ollama_url = Column(String(500), nullable=True)
    ollama_model = Column(String(200), nullable=True)
    ollama_embeddings_model = Column(String(200), nullable=True)

    # Configurações RAG (Retrieval-Augmented Generation)
    rag_chunk_size = Column(Integer, default=1500)  # Tamanho dos chunks de texto
    rag_chunk_overlap = Column(Integer, default=200)  # Sobreposição entre chunks
    rag_search_limit = Column(Integer, default=5)  # Número de documentos recuperados
    rag_num_predict = Column(Integer, default=800)  # Tokens máximos na resposta
    rag_temperature = Column(Float, default=0.6)  # Criatividade (0.0-1.0)
    rag_top_p = Column(Float, default=0.9)  # Nucleus sampling (0.0-1.0)

    # Metadados
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Manter compatibilidade com código antigo (aliases)
PlanType = TipoPlano
PlanPeriod = PeriodoPlano
OrderStatus = StatusPedido
Plan = Plano
Client = Cliente
Order = Pedido
