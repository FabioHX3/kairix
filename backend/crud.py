from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import models
import schemas
from datetime import datetime, date


# ============= PLANS =============
def get_plan(db: Session, plan_id: int) -> Optional[models.Plano]:
    return db.query(models.Plano).filter(models.Plano.id == plan_id).first()


def get_plans(db: Session, skip: int = 0, limit: int = 100, is_active: bool = None) -> List[models.Plano]:
    query = db.query(models.Plano)
    if is_active is not None:
        query = query.filter(models.Plano.ativo == is_active)
    return query.offset(skip).limit(limit).all()


def get_plans_by_type(db: Session, plan_type: models.TipoPlano) -> List[models.Plano]:
    return db.query(models.Plano).filter(
        models.Plano.tipo == plan_type,
        models.Plano.ativo == True
    ).all()


def create_plan(db: Session, plan: schemas.PlanCreate) -> models.Plano:
    db_plan = models.Plano(**plan.model_dump())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def update_plan(db: Session, plan_id: int, plan: schemas.PlanUpdate) -> Optional[models.Plano]:
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return None

    update_data = plan.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_plan, key, value)

    db_plan.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_plan)
    return db_plan


def delete_plan(db: Session, plan_id: int) -> bool:
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return False
    db.delete(db_plan)
    db.commit()
    return True


# ============= CLIENTS =============
def get_client(db: Session, client_id: int) -> Optional[models.Cliente]:
    return db.query(models.Cliente).filter(models.Cliente.id == client_id).first()


def get_client_by_email(db: Session, email: str) -> Optional[models.Cliente]:
    return db.query(models.Cliente).filter(models.Cliente.email == email).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Cliente]:
    return db.query(models.Cliente).offset(skip).limit(limit).all()


def create_client(db: Session, client: schemas.ClientCreate) -> models.Cliente:
    import bcrypt

    # Extrair dados e remover senha do dict
    client_data = client.model_dump()
    senha = client_data.pop('senha')

    # Hash da senha com bcrypt
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Criar cliente com senha hashada e DESATIVADO (ativa só após pagamento)
    db_client = models.Cliente(**client_data, senha_hash=senha_hash, ativo=False)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, client: schemas.ClientUpdate) -> Optional[models.Cliente]:
    db_client = get_client(db, client_id)
    if not db_client:
        return None

    update_data = client.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)

    db_client.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_client)
    return db_client


# ============= ORDERS =============
def get_order(db: Session, order_id: int) -> Optional[models.Pedido]:
    return db.query(models.Pedido).filter(models.Pedido.id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Pedido]:
    return db.query(models.Pedido).order_by(desc(models.Pedido.criado_em)).offset(skip).limit(limit).all()


def get_orders_by_client(db: Session, client_id: int) -> List[models.Pedido]:
    return db.query(models.Pedido).filter(models.Pedido.cliente_id == client_id).order_by(desc(models.Pedido.criado_em)).all()


def get_orders_by_status(db: Session, status: models.StatusPedido) -> List[models.Pedido]:
    return db.query(models.Pedido).filter(models.Pedido.status == status).order_by(desc(models.Pedido.criado_em)).all()


def create_order(db: Session, order: schemas.OrderCreate) -> models.Pedido:
    db_order = models.Pedido(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order: schemas.OrderUpdate) -> Optional[models.Pedido]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    update_data = order.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_order, key, value)

    db_order.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(db: Session, order_id: int, status_update: schemas.OrderStatusUpdate) -> Optional[models.Pedido]:
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    db_order.status = status_update.status
    db_order.atualizado_em = datetime.utcnow()

    db.commit()
    db.refresh(db_order)
    return db_order


# ============= CONVERSAS =============
def get_conversa(db: Session, conversa_id: int) -> Optional[models.Conversa]:
    return db.query(models.Conversa).filter(models.Conversa.id == conversa_id).first()


def get_conversa_by_numero(db: Session, pedido_id: int, contato_numero: str) -> Optional[models.Conversa]:
    """Busca conversa ativa de um contato específico"""
    return db.query(models.Conversa).filter(
        models.Conversa.pedido_id == pedido_id,
        models.Conversa.contato_numero == contato_numero,
        models.Conversa.status == models.StatusConversa.ATIVA
    ).first()


def get_conversas_by_pedido(
    db: Session,
    pedido_id: int,
    skip: int = 0,
    limit: int = 100,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None
) -> List[models.Conversa]:
    query = db.query(models.Conversa).filter(
        models.Conversa.pedido_id == pedido_id
    )

    # Aplicar filtros de data se fornecidos
    if data_inicio:
        query = query.filter(models.Conversa.criado_em >= datetime.combine(data_inicio, datetime.min.time()))
    if data_fim:
        query = query.filter(models.Conversa.criado_em <= datetime.combine(data_fim, datetime.max.time()))

    return query.order_by(desc(models.Conversa.ultima_interacao)).offset(skip).limit(limit).all()


def create_conversa(db: Session, conversa: schemas.ConversaCriar) -> models.Conversa:
    db_conversa = models.Conversa(**conversa.model_dump())
    db.add(db_conversa)
    db.commit()
    db.refresh(db_conversa)
    return db_conversa


def update_conversa(db: Session, conversa_id: int, conversa: schemas.ConversaAtualizar) -> Optional[models.Conversa]:
    db_conversa = get_conversa(db, conversa_id)
    if not db_conversa:
        return None

    update_data = conversa.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_conversa, key, value)

    db_conversa.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_conversa)
    return db_conversa


def update_conversa_metricas(db: Session, conversa_id: int) -> Optional[models.Conversa]:
    """Atualiza métricas calculadas da conversa"""
    db_conversa = get_conversa(db, conversa_id)
    if not db_conversa:
        return None

    # Contar mensagens
    total_msgs = db.query(models.Mensagem).filter(models.Mensagem.conversa_id == conversa_id).count()
    msgs_bot = db.query(models.Mensagem).filter(
        models.Mensagem.conversa_id == conversa_id,
        models.Mensagem.direcao == models.DirecaoMensagem.ENVIADA
    ).count()
    msgs_usuario = db.query(models.Mensagem).filter(
        models.Mensagem.conversa_id == conversa_id,
        models.Mensagem.direcao == models.DirecaoMensagem.RECEBIDA
    ).count()

    # Calcular tempo médio de resposta
    mensagens_com_tempo = db.query(models.Mensagem).filter(
        models.Mensagem.conversa_id == conversa_id,
        models.Mensagem.tempo_resposta.isnot(None)
    ).all()

    tempo_medio = None
    if mensagens_com_tempo:
        tempos = [m.tempo_resposta for m in mensagens_com_tempo if m.tempo_resposta]
        if tempos:
            tempo_medio = sum(tempos) / len(tempos)

    # Atualizar conversa
    db_conversa.total_mensagens = total_msgs
    db_conversa.mensagens_bot = msgs_bot
    db_conversa.mensagens_usuario = msgs_usuario
    db_conversa.tempo_resposta_medio = tempo_medio
    db_conversa.ultima_interacao = datetime.utcnow()
    db_conversa.atualizado_em = datetime.utcnow()

    db.commit()
    db.refresh(db_conversa)
    return db_conversa


# ============= MENSAGENS =============
def get_mensagem(db: Session, mensagem_id: int) -> Optional[models.Mensagem]:
    return db.query(models.Mensagem).filter(models.Mensagem.id == mensagem_id).first()


def get_mensagem_by_evolution_id(db: Session, evolution_message_id: str) -> Optional[models.Mensagem]:
    return db.query(models.Mensagem).filter(
        models.Mensagem.evolution_message_id == evolution_message_id
    ).first()


def get_mensagens_by_conversa(db: Session, conversa_id: int, skip: int = 0, limit: int = 100) -> List[models.Mensagem]:
    return db.query(models.Mensagem).filter(
        models.Mensagem.conversa_id == conversa_id
    ).order_by(models.Mensagem.timestamp).offset(skip).limit(limit).all()


def create_mensagem(db: Session, mensagem: schemas.MensagemCriar) -> models.Mensagem:
    db_mensagem = models.Mensagem(**mensagem.model_dump())
    db.add(db_mensagem)
    db.commit()
    db.refresh(db_mensagem)

    # Atualizar métricas da conversa
    update_conversa_metricas(db, mensagem.conversa_id)

    return db_mensagem


def update_mensagem(db: Session, mensagem_id: int, mensagem: schemas.MensagemAtualizar) -> Optional[models.Mensagem]:
    db_mensagem = get_mensagem(db, mensagem_id)
    if not db_mensagem:
        return None

    update_data = mensagem.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mensagem, key, value)

    db.commit()
    db.refresh(db_mensagem)
    return db_mensagem


# ============= MÉTRICAS =============
def calcular_metricas_diarias(db: Session, pedido_id: int, data: datetime.date) -> models.MetricaDiaria:
    """Calcula métricas diárias para um pedido em uma data específica"""
    from sqlalchemy import func, and_

    # Buscar ou criar métrica
    metrica = db.query(models.MetricaDiaria).filter(
        models.MetricaDiaria.pedido_id == pedido_id,
        models.MetricaDiaria.data == data
    ).first()

    if not metrica:
        metrica = models.MetricaDiaria(pedido_id=pedido_id, data=data)
        db.add(metrica)

    # Calcular métricas
    data_inicio = datetime.combine(data, datetime.min.time())
    data_fim = datetime.combine(data, datetime.max.time())

    # Total de mensagens
    total_mensagens = db.query(func.count(models.Mensagem.id)).join(
        models.Conversa
    ).filter(
        models.Conversa.pedido_id == pedido_id,
        models.Mensagem.timestamp >= data_inicio,
        models.Mensagem.timestamp <= data_fim
    ).scalar() or 0

    # Total de contatos únicos
    total_contatos = db.query(func.count(func.distinct(models.Conversa.contato_numero))).filter(
        models.Conversa.pedido_id == pedido_id,
        models.Conversa.iniciada_em >= data_inicio,
        models.Conversa.iniciada_em <= data_fim
    ).scalar() or 0

    # Conversas iniciadas
    conversas_iniciadas = db.query(func.count(models.Conversa.id)).filter(
        models.Conversa.pedido_id == pedido_id,
        models.Conversa.iniciada_em >= data_inicio,
        models.Conversa.iniciada_em <= data_fim
    ).scalar() or 0

    # Conversas finalizadas
    conversas_finalizadas = db.query(func.count(models.Conversa.id)).filter(
        models.Conversa.pedido_id == pedido_id,
        models.Conversa.finalizada_em >= data_inicio,
        models.Conversa.finalizada_em <= data_fim,
        models.Conversa.status == models.StatusConversa.FINALIZADA
    ).scalar() or 0

    # Tempo médio de resposta
    tempos_resposta = db.query(models.Mensagem.tempo_resposta).join(
        models.Conversa
    ).filter(
        models.Conversa.pedido_id == pedido_id,
        models.Mensagem.timestamp >= data_inicio,
        models.Mensagem.timestamp <= data_fim,
        models.Mensagem.tempo_resposta.isnot(None)
    ).all()

    tempo_resposta_medio = 0.0
    if tempos_resposta:
        tempos = [t[0] for t in tempos_resposta if t[0] is not None]
        if tempos:
            tempo_resposta_medio = sum(tempos) / len(tempos)

    # Atualizar métrica
    metrica.total_mensagens = total_mensagens
    metrica.total_contatos = total_contatos
    metrica.conversas_iniciadas = conversas_iniciadas
    metrica.conversas_finalizadas = conversas_finalizadas
    metrica.tempo_resposta_medio = tempo_resposta_medio
    metrica.atualizado_em = datetime.utcnow()

    db.commit()
    db.refresh(metrica)

    return metrica


def get_metricas_periodo(
    db: Session,
    pedido_id: int,
    data_inicio: datetime.date,
    data_fim: datetime.date
) -> List[models.MetricaDiaria]:
    """Busca métricas de um período"""
    return db.query(models.MetricaDiaria).filter(
        models.MetricaDiaria.pedido_id == pedido_id,
        models.MetricaDiaria.data >= data_inicio,
        models.MetricaDiaria.data <= data_fim
    ).order_by(models.MetricaDiaria.data).all()


# ============= CONFIGURAÇÕES DO SISTEMA =============

def get_configuracao_sistema(db: Session):
    """
    Busca as configurações do sistema.
    Retorna a primeira configuração ou cria uma vazia se não existir.
    """
    config = db.query(models.ConfiguracaoSistema).first()
    if not config:
        config = models.ConfiguracaoSistema()
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def update_configuracao_sistema(
    db: Session,
    configuracao: schemas.ConfiguracaoSistemaAtualizar
):
    """
    Atualiza as configurações do sistema.
    """
    db_config = get_configuracao_sistema(db)

    # Atualizar campos não nulos
    update_data = configuracao.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)

    db_config.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(db_config)
    return db_config
