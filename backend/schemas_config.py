from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ============= AGENTE NORMAL =============
class RespostaPredefinida(BaseModel):
    pergunta: str
    resposta: str
    palavras_chave: Optional[List[str]] = []


class OpcaoMenu(BaseModel):
    numero: str
    titulo: str
    acao: str  # 'resposta', 'submenu', 'transferir'
    conteudo: Optional[str] = None


class ConfigAgenteNormal(BaseModel):
    # Configurações básicas
    mensagem_boas_vindas: str = "Olá! Bem-vindo ao nosso atendimento automático."
    mensagem_fora_horario: Optional[str] = None
    horario_inicio: str = "08:00"
    horario_fim: str = "18:00"
    dias_semana: List[int] = [1, 2, 3, 4, 5]  # 1=Segunda, 7=Domingo

    # WhatsApp
    numero_whatsapp: Optional[str] = None
    api_key_whatsapp: Optional[str] = None

    # Respostas e Menu
    respostas_predefinidas: List[RespostaPredefinida] = []
    menu_opcoes: List[OpcaoMenu] = []

    # Transferência
    numero_transferencia: Optional[str] = None
    mensagem_transferencia: str = "Aguarde, você será transferido para um atendente."


# ============= AGENTE COM IA =============
class DocumentoBaseConhecimento(BaseModel):
    nome: str
    url: Optional[str] = None
    tamanho_mb: float = 0
    tipo: str  # 'pdf', 'txt', 'docx', 'csv'
    data_upload: Optional[str] = None


class ConfigAgenteIA(ConfigAgenteNormal):
    # Configurações de IA
    personalidade: str = "profissional e prestativo"
    contexto_adicional: str = ""
    temperatura: float = 0.7  # Criatividade (0-1)

    # Base de conhecimento
    documentos: List[DocumentoBaseConhecimento] = []
    tamanho_total_mb: float = 0
    limite_mb: float = 100  # Varia por plano

    # Limites
    limite_interacoes_mes: int = 1000  # Varia por plano
    interacoes_usadas: int = 0

    # Fine-tuning (Enterprise)
    fine_tuning_ativo: bool = False
    modelo_customizado_id: Optional[str] = None


# ============= AGENTE FINANCEIRO =============
class ConfigAgenteFinanceiro(ConfigAgenteNormal):
    # Configurações financeiras específicas
    moeda: str = "BRL"
    formato_numero: str = "pt-BR"

    # Integrações financeiras
    api_gateway_pagamento: Optional[str] = None
    api_key_gateway: Optional[str] = None

    # Notificações
    notificar_pagamentos: bool = True
    email_notificacao: Optional[str] = None


# ============= RESPOSTA GENÉRICA =============
class ConfiguracaoResponse(BaseModel):
    pedido_id: int
    tipo_agente: str
    configuracao: Dict[str, Any]
    configurado: bool = False
    ultima_atualizacao: Optional[str] = None


class ConfiguracaoUpdate(BaseModel):
    configuracao: Dict[str, Any]
