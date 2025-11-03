from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from models import TipoPlano, PeriodoPlano, StatusPedido, StatusConversa, TipoMensagem, DirecaoMensagem


# Plan Schemas
class PlanoBase(BaseModel):
    nome: str
    tipo: TipoPlano
    periodo: PeriodoPlano
    preco: float
    preco_antigo: Optional[float] = None
    descricao: Optional[str] = None
    recursos: Optional[str] = None
    destaque: bool = False
    ativo: bool = True


class PlanoCriar(PlanoBase):
    pass


class PlanoAtualizar(BaseModel):
    nome: Optional[str] = None
    preco: Optional[float] = None
    preco_antigo: Optional[float] = None
    descricao: Optional[str] = None
    recursos: Optional[str] = None
    destaque: Optional[bool] = None
    ativo: Optional[bool] = None


class Plano(PlanoBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


# Client Schemas
class ClienteBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=200)
    email: EmailStr
    telefone: str = Field(..., min_length=10, max_length=20)
    whatsapp: str = Field(..., min_length=10, max_length=20)
    nome_empresa: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)


class ClienteBaseComSenha(ClienteBase):
    senha: str = Field(..., min_length=6, max_length=50)  # Senha em texto plano (será hashada)


class ClienteCriar(ClienteBaseComSenha):
    pass


class ClienteAtualizar(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    whatsapp: Optional[str] = Field(None, min_length=10, max_length=20)
    nome_empresa: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)
    ativo: Optional[bool] = None


class Cliente(ClienteBase):
    id: int
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


# Order Schemas
class PedidoBase(BaseModel):
    cliente_id: int
    plano_id: int
    valor: float
    desconto: float = 0
    total: float
    observacoes: Optional[str] = None


class PedidoCriar(PedidoBase):
    pass


class PedidoAtualizar(BaseModel):
    status: Optional[StatusPedido] = None
    metodo_pagamento: Optional[str] = None
    gateway_id: Optional[str] = None
    link_pagamento: Optional[str] = None
    data_pagamento: Optional[datetime] = None
    observacoes: Optional[str] = None
    configuracao_agente: Optional[str] = None


class PedidoStatusAtualizar(BaseModel):
    status: StatusPedido
    observacoes: Optional[str] = None


class Pedido(PedidoBase):
    id: int
    status: StatusPedido
    metodo_pagamento: Optional[str]
    gateway_id: Optional[str]
    link_pagamento: Optional[str]
    data_pagamento: Optional[datetime]
    configuracao_agente: Optional[str]
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class PedidoComDetalhes(Pedido):
    cliente: Cliente
    plano: Plano


# Combined Schemas for Registration
class RegistroCliente(BaseModel):
    cliente: ClienteCriar
    plano_id: int


class RespostaRegistro(BaseModel):
    cliente: Cliente
    pedido: Pedido
    link_pagamento: str


# ============= SISTEMA DE CONVERSAS =============

# Mensagem Schemas
class MensagemBase(BaseModel):
    tipo: TipoMensagem = TipoMensagem.TEXTO
    direcao: DirecaoMensagem
    conteudo: Optional[str] = None
    midia_url: Optional[str] = None
    midia_mimetype: Optional[str] = None
    respondida_por_bot: bool = False
    tempo_resposta: Optional[float] = None


class MensagemCriar(MensagemBase):
    conversa_id: int
    evolution_message_id: Optional[str] = None
    evolution_push_name: Optional[str] = None


class MensagemAtualizar(BaseModel):
    lida: Optional[bool] = None
    erro: Optional[str] = None


class Mensagem(MensagemBase):
    id: int
    conversa_id: int
    lida: Optional[bool] = False
    erro: Optional[str] = None
    evolution_message_id: Optional[str] = None
    evolution_push_name: Optional[str] = None
    timestamp: datetime
    criado_em: datetime

    class Config:
        from_attributes = True


# Conversa Schemas
class ConversaBase(BaseModel):
    contato_nome: str
    contato_numero: str
    contato_foto_url: Optional[str] = None
    status: StatusConversa = StatusConversa.ATIVA
    contexto: Optional[str] = None
    tags: Optional[str] = None


class ConversaCriar(ConversaBase):
    pedido_id: int
    evolution_remote_jid: Optional[str] = None
    evolution_instance: Optional[str] = None


class ConversaAtualizar(BaseModel):
    status: Optional[StatusConversa] = None
    contexto: Optional[str] = None
    tags: Optional[str] = None
    finalizada_em: Optional[datetime] = None


class Conversa(ConversaBase):
    id: int
    pedido_id: int
    total_mensagens: Optional[int] = 0
    mensagens_bot: Optional[int] = 0
    mensagens_usuario: Optional[int] = 0
    tempo_primeira_resposta: Optional[float] = None
    tempo_resposta_medio: Optional[float] = None
    evolution_remote_jid: Optional[str] = None
    evolution_instance: Optional[str] = None
    iniciada_em: datetime
    finalizada_em: Optional[datetime] = None
    ultima_interacao: datetime
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


class ConversaComMensagens(Conversa):
    mensagens: List[Mensagem] = []


# Métrica Diária Schema
class MetricaDiariaBase(BaseModel):
    pedido_id: int
    data: date
    total_mensagens: int = 0
    total_contatos: int = 0
    conversas_iniciadas: int = 0
    conversas_finalizadas: int = 0
    tempo_resposta_medio: float = 0.0
    taxa_conversao: float = 0.0


class MetricaDiaria(MetricaDiariaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


# ============= CONFIGURAÇÕES DO SISTEMA =============

class ConfiguracaoSistemaBase(BaseModel):
    # Evolution API (configurações globais)
    evolution_api_url: Optional[str] = None
    evolution_api_key: Optional[str] = None
    kairix_public_url: Optional[str] = None

    # Qdrant (Base de Conhecimento Vetorizada)
    qdrant_url: Optional[str] = None
    qdrant_api_key: Optional[str] = None
    qdrant_collection: Optional[str] = None

    # Ollama (IA Local) - único provider usado
    ollama_url: Optional[str] = None
    ollama_model: Optional[str] = None
    ollama_embeddings_model: Optional[str] = None


class ConfiguracaoSistemaCriar(ConfiguracaoSistemaBase):
    pass


class ConfiguracaoSistemaAtualizar(ConfiguracaoSistemaBase):
    pass


class ConfiguracaoSistema(ConfiguracaoSistemaBase):
    id: int
    criado_em: datetime
    atualizado_em: datetime

    class Config:
        from_attributes = True


# Aliases para compatibilidade com código antigo
PlanBase = PlanoBase
PlanCreate = PlanoCriar
PlanUpdate = PlanoAtualizar
Plan = Plano

ClientBase = ClienteBase
ClientCreate = ClienteCriar
ClientUpdate = ClienteAtualizar
Client = Cliente

OrderBase = PedidoBase
OrderCreate = PedidoCriar
OrderUpdate = PedidoAtualizar
OrderStatusUpdate = PedidoStatusAtualizar
Order = Pedido
OrderWithDetails = PedidoComDetalhes

ClientRegistration = RegistroCliente
RegistrationResponse = RespostaRegistro
