"""
Router para painel administrativo
Gerencia clientes, planos, pedidos e configurações do sistema
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import bcrypt
import models
import schemas
from database import get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ============ AUTENTICAÇÃO ADMIN ============

class AdminLoginRequest(BaseModel):
    email: EmailStr
    senha: str


class AdminLoginResponse(BaseModel):
    admin_id: int
    nome: str
    email: str


@router.post("/login", response_model=AdminLoginResponse)
def admin_login(credentials: AdminLoginRequest, db: Session = Depends(get_db)):
    """Autentica um administrador"""

    # Buscar admin por email
    admin = db.query(models.Administrador).filter(
        models.Administrador.email == credentials.email
    ).first()

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

    if not admin.ativo:
        raise HTTPException(
            status_code=403,
            detail="Administrador desativado"
        )

    # Verificar senha
    try:
        senha_correta = bcrypt.checkpw(
            credentials.senha.encode('utf-8'),
            admin.senha_hash.encode('utf-8')
        )

        if not senha_correta:
            raise HTTPException(
                status_code=401,
                detail="Email ou senha incorretos"
            )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Erro ao verificar credenciais"
        )

    return AdminLoginResponse(
        admin_id=admin.id,
        nome=admin.nome,
        email=admin.email
    )


# ============ DASHBOARD / RESUMO ============

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Estatísticas gerais para o dashboard administrativo"""

    # Total de clientes
    total_clientes = db.query(func.count(models.Cliente.id)).scalar()
    clientes_ativos = db.query(func.count(models.Cliente.id)).filter(models.Cliente.ativo == True).scalar()

    # Total de pedidos
    total_pedidos = db.query(func.count(models.Pedido.id)).scalar()
    pedidos_concluidos = db.query(func.count(models.Pedido.id)).filter(
        models.Pedido.status == models.StatusPedido.CONCLUIDO
    ).scalar()

    # Receita total
    receita_total = db.query(func.sum(models.Pedido.total)).filter(
        models.Pedido.status.in_([
            models.StatusPedido.PAGAMENTO_APROVADO,
            models.StatusPedido.CONFIGURANDO_AMBIENTE,
            models.StatusPedido.INSTALANDO_AGENTE,
            models.StatusPedido.CONCLUIDO
        ])
    ).scalar() or 0

    # Receita do mês atual
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    receita_mes = db.query(func.sum(models.Pedido.total)).filter(
        models.Pedido.status.in_([
            models.StatusPedido.PAGAMENTO_APROVADO,
            models.StatusPedido.CONFIGURANDO_AMBIENTE,
            models.StatusPedido.INSTALANDO_AGENTE,
            models.StatusPedido.CONCLUIDO
        ]),
        models.Pedido.criado_em >= inicio_mes
    ).scalar() or 0

    # Pedidos por status
    pedidos_por_status = {}
    for status in models.StatusPedido:
        count = db.query(func.count(models.Pedido.id)).filter(
            models.Pedido.status == status
        ).scalar()
        pedidos_por_status[status.value] = count

    # Clientes inativos
    clientes_inativos = db.query(func.count(models.Cliente.id)).filter(models.Cliente.ativo == False).scalar()

    # Aguardando pagamento
    aguardando_pagamento = db.query(func.count(models.Pedido.id)).filter(
        models.Pedido.status == models.StatusPedido.AGUARDANDO_PAGAMENTO
    ).scalar()

    # Total de conversas
    total_conversas = db.query(func.count(models.Conversa.id)).scalar() or 0

    # Últimos 5 pedidos (com cliente e plano)
    from sqlalchemy.orm import joinedload
    ultimos_pedidos = db.query(models.Pedido)\
        .options(joinedload(models.Pedido.cliente))\
        .options(joinedload(models.Pedido.plano))\
        .order_by(desc(models.Pedido.criado_em))\
        .limit(5)\
        .all()

    return {
        "total_clientes": total_clientes,
        "clientes_ativos": clientes_ativos,
        "clientes_inativos": clientes_inativos,
        "aguardando_pagamento": aguardando_pagamento,
        "total_conversas": total_conversas,
        "total_pedidos": total_pedidos,
        "pedidos_concluidos": pedidos_concluidos,
        "receita_total": receita_total,
        "receita_mes": receita_mes,
        "pedidos_por_status": pedidos_por_status,
        "ultimos_pedidos": ultimos_pedidos
    }


@router.get("/metricas-graficos")
def get_metricas_graficos(db: Session = Depends(get_db)):
    """Dados para gráficos do dashboard"""
    from datetime import date, timedelta

    hoje = date.today()

    # === CONVERSAS DIÁRIAS (Últimos 7 dias) ===
    conversas_labels = []
    conversas_data = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        inicio_dia = datetime.combine(dia, datetime.min.time())
        fim_dia = datetime.combine(dia, datetime.max.time())

        count = db.query(func.count(models.Conversa.id)).filter(
            models.Conversa.iniciada_em >= inicio_dia,
            models.Conversa.iniciada_em <= fim_dia
        ).scalar() or 0

        conversas_labels.append(dia.strftime("%d/%m"))
        conversas_data.append(count)

    # === MENSAGENS DIÁRIAS (Últimos 7 dias) ===
    mensagens_labels = []
    mensagens_data = []
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        inicio_dia = datetime.combine(dia, datetime.min.time())
        fim_dia = datetime.combine(dia, datetime.max.time())

        count = db.query(func.count(models.Mensagem.id)).filter(
            models.Mensagem.timestamp >= inicio_dia,
            models.Mensagem.timestamp <= fim_dia
        ).scalar() or 0

        mensagens_labels.append(dia.strftime("%d/%m"))
        mensagens_data.append(count)

    # === NOVOS CLIENTES (Últimos 30 dias) ===
    clientes_labels = []
    clientes_data = []
    for i in range(29, -1, -1):
        dia = hoje - timedelta(days=i)
        inicio_dia = datetime.combine(dia, datetime.min.time())
        fim_dia = datetime.combine(dia, datetime.max.time())

        count = db.query(func.count(models.Cliente.id)).filter(
            models.Cliente.criado_em >= inicio_dia,
            models.Cliente.criado_em <= fim_dia
        ).scalar() or 0

        # Mostrar apenas a cada 5 dias para não poluir
        if i % 5 == 0 or i == 0:
            clientes_labels.append(dia.strftime("%d/%m"))
        else:
            clientes_labels.append("")
        clientes_data.append(count)

    # === RECEITA MENSAL (Últimos 6 meses) ===
    receita_labels = []
    receita_data = []
    for i in range(5, -1, -1):
        # Calcular o mês
        mes_ref = hoje.replace(day=1) - timedelta(days=i * 30)
        inicio_mes = mes_ref.replace(day=1)

        # Próximo mês
        if mes_ref.month == 12:
            fim_mes = mes_ref.replace(year=mes_ref.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            fim_mes = mes_ref.replace(month=mes_ref.month + 1, day=1) - timedelta(days=1)

        inicio_mes_dt = datetime.combine(inicio_mes, datetime.min.time())
        fim_mes_dt = datetime.combine(fim_mes, datetime.max.time())

        total = db.query(func.sum(models.Pedido.total)).filter(
            models.Pedido.status.in_([
                models.StatusPedido.PAGAMENTO_APROVADO,
                models.StatusPedido.CONFIGURANDO_AMBIENTE,
                models.StatusPedido.INSTALANDO_AGENTE,
                models.StatusPedido.CONCLUIDO
            ]),
            models.Pedido.data_pagamento >= inicio_mes_dt,
            models.Pedido.data_pagamento <= fim_mes_dt
        ).scalar() or 0

        receita_labels.append(mes_ref.strftime("%b/%y"))
        receita_data.append(float(total))

    return {
        "conversas": {
            "labels": conversas_labels,
            "data": conversas_data
        },
        "mensagens": {
            "labels": mensagens_labels,
            "data": mensagens_data
        },
        "novos_clientes": {
            "labels": clientes_labels,
            "data": clientes_data
        },
        "receita_mensal": {
            "labels": receita_labels,
            "data": receita_data
        }
    }


# ============ GESTÃO DE CLIENTES ============

@router.get("/clientes")
def list_all_clients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar todos os clientes com filtros"""
    query = db.query(models.Cliente)

    if search:
        query = query.filter(
            (models.Cliente.nome.ilike(f"%{search}%")) |
            (models.Cliente.email.ilike(f"%{search}%")) |
            (models.Cliente.telefone.ilike(f"%{search}%"))
        )

    if ativo is not None:
        query = query.filter(models.Cliente.ativo == ativo)

    clientes = query.offset(skip).limit(limit).all()

    # Adicionar plano atual de cada cliente (último pedido independente do status)
    resultado = []
    for cliente in clientes:
        # Buscar o pedido mais recente do cliente (sem filtro de status)
        ultimo_pedido = db.query(models.Pedido).filter(
            models.Pedido.cliente_id == cliente.id
        ).order_by(models.Pedido.id.desc()).first()

        # Extrair informações do plano
        plano_nome = None
        plano_periodo = None
        data_validade = None

        if ultimo_pedido and ultimo_pedido.plano:
            plano_nome = ultimo_pedido.plano.nome
            plano_periodo = ultimo_pedido.plano.periodo.value if ultimo_pedido.plano.periodo else None
            data_validade = ultimo_pedido.data_validade.isoformat() if ultimo_pedido.data_validade else None

        cliente_dict = {
            "id": cliente.id,
            "nome": cliente.nome,
            "email": cliente.email,
            "telefone": cliente.telefone,
            "nome_empresa": cliente.nome_empresa,
            "cpf_cnpj": cliente.cpf_cnpj,
            "endereco": cliente.endereco,
            "cidade": cliente.cidade,
            "estado": cliente.estado,
            "cep": cliente.cep,
            "whatsapp": cliente.whatsapp,
            "ativo": cliente.ativo,
            "criado_em": cliente.criado_em,
            "atualizado_em": cliente.atualizado_em,
            "plano_atual": plano_nome,
            "plano_periodo": plano_periodo,
            "data_validade": data_validade
        }
        resultado.append(cliente_dict)

    return resultado


@router.get("/clientes/{client_id}")
def get_client_details(client_id: int, db: Session = Depends(get_db)):
    """Detalhes completos de um cliente incluindo pedidos"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar pedidos do cliente
    pedidos = db.query(models.Pedido).filter(models.Pedido.cliente_id == client_id).all()

    return {
        "cliente": cliente,
        "pedidos": pedidos,
        "total_pedidos": len(pedidos),
        "receita_total": sum(p.total for p in pedidos)
    }


@router.put("/clientes/{client_id}")
def update_client(client_id: int, updates: dict, db: Session = Depends(get_db)):
    """Atualizar dados de um cliente"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Atualizar campos permitidos
    allowed_fields = ["nome", "email", "telefone", "nome_empresa", "cpf_cnpj",
                      "endereco", "cidade", "estado", "cep", "whatsapp", "ativo"]

    for field, value in updates.items():
        if field in allowed_fields and hasattr(cliente, field):
            setattr(cliente, field, value)

    cliente.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(cliente)

    return cliente


@router.delete("/clientes/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Excluir cliente e todos seus pedidos (cascade delete)"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar todos os pedidos do cliente
    pedidos = db.query(models.Pedido).filter(models.Pedido.cliente_id == client_id).all()

    # Excluir todos os pedidos primeiro
    for pedido in pedidos:
        # Excluir configurações do bot se existirem
        config = db.query(models.ConfiguracaoBot).filter(
            models.ConfiguracaoBot.pedido_id == pedido.id
        ).first()
        if config:
            db.delete(config)

        # Excluir conversas e mensagens do pedido
        conversas = db.query(models.Conversa).filter(models.Conversa.pedido_id == pedido.id).all()
        for conversa in conversas:
            # Mensagens serão excluídas automaticamente por cascade
            db.delete(conversa)

        # Excluir o pedido
        db.delete(pedido)

    # Excluir o cliente
    db.delete(cliente)
    db.commit()

    return {"message": f"Cliente {cliente.nome} e {len(pedidos)} pedido(s) excluído(s) com sucesso"}


@router.get("/clientes/{client_id}/pedidos")
def get_client_orders(client_id: int, db: Session = Depends(get_db)):
    """Buscar apenas os pedidos de um cliente com join para plano"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    pedidos = db.query(models.Pedido).filter(models.Pedido.cliente_id == client_id).all()

    # Serializar pedidos com plano
    pedidos_list = []
    for pedido in pedidos:
        pedido_dict = {
            "id": pedido.id,
            "cliente_id": pedido.cliente_id,
            "plano_id": pedido.plano_id,
            "status": pedido.status.value,
            "metodo_pagamento": pedido.metodo_pagamento,
            "gateway_id": pedido.gateway_id,
            "link_pagamento": pedido.link_pagamento,
            "data_pagamento": pedido.data_pagamento.isoformat() if pedido.data_pagamento else None,
            "data_validade": pedido.data_validade.isoformat() if pedido.data_validade else None,
            "valor": pedido.valor,
            "desconto": pedido.desconto,
            "total": pedido.total,
            "observacoes": pedido.observacoes,
            "configuracao_agente": pedido.configuracao_agente,
            "criado_em": pedido.criado_em.isoformat(),
            "atualizado_em": pedido.atualizado_em.isoformat(),
            "plano": {
                "id": pedido.plano.id,
                "nome": pedido.plano.nome,
                "tipo": pedido.plano.tipo.value,
                "periodo": pedido.plano.periodo.value,
                "preco": pedido.plano.preco
            } if pedido.plano else None
        }
        pedidos_list.append(pedido_dict)

    return pedidos_list


@router.post("/clientes/{client_id}/toggle")
def toggle_client(client_id: int, data: dict, db: Session = Depends(get_db)):
    """Ativar/desativar um cliente"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    novo_status = data.get("ativo", not cliente.ativo)
    estava_inativo = not cliente.ativo

    cliente.ativo = novo_status
    cliente.atualizado_em = datetime.utcnow()

    response_data = {
        "message": f"Cliente {'ativado' if cliente.ativo else 'desativado'} com sucesso",
        "cliente": cliente
    }

    # Se está ATIVANDO um cliente que estava inativo, fazer o mesmo que o webhook faz
    if novo_status and estava_inativo:
        # Buscar pedido mais recente do cliente
        pedido = db.query(models.Pedido).filter(
            models.Pedido.cliente_id == client_id
        ).order_by(models.Pedido.id.desc()).first()

        if pedido:
            # Criar ou atualizar configuração do bot
            config = db.query(models.ConfiguracaoBot).filter(
                models.ConfiguracaoBot.pedido_id == pedido.id
            ).first()

            if not config:
                config = models.ConfiguracaoBot(
                    pedido_id=pedido.id,
                    ativo=True
                )
                db.add(config)
                db.flush()

            # Criar instância no Evolution API automaticamente
            from services import evolution_helper
            import asyncio

            evolution_result = None
            try:
                evolution_result = asyncio.run(evolution_helper.criar_instancia_evolution(db, cliente, pedido))

                if evolution_result and evolution_result.get("success"):
                    print(f"✅ Instância Evolution criada: {evolution_result.get('instance_name')}")
                    response_data["evolution_instance"] = {
                        "created": True,
                        "instance_name": evolution_result.get("instance_name"),
                        "numero": evolution_result.get("numero")
                    }
                else:
                    print(f"⚠️ Falha ao criar instância Evolution: {evolution_result.get('error') if evolution_result else 'Erro desconhecido'}")
                    response_data["evolution_instance"] = {
                        "created": False,
                        "error": evolution_result.get("error") if evolution_result else "Erro desconhecido"
                    }
            except Exception as e:
                print(f"❌ Exceção ao criar instância Evolution: {str(e)}")
                response_data["evolution_instance"] = {
                    "created": False,
                    "error": str(e)
                }

    db.commit()
    db.refresh(cliente)

    return response_data


@router.delete("/clientes/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Desativar um cliente (soft delete)"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == client_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Não deletar, apenas desativar
    cliente.ativo = False
    cliente.atualizado_em = datetime.utcnow()
    db.commit()

    return {"message": "Cliente desativado com sucesso"}


# ============ GESTÃO DE PLANOS ============

@router.get("/planos")
def list_all_plans(
    tipo: Optional[str] = None,
    periodo: Optional[str] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listar todos os planos com filtros"""
    query = db.query(models.Plano)

    if tipo:
        query = query.filter(models.Plano.tipo == tipo)

    if periodo:
        query = query.filter(models.Plano.periodo == periodo)

    if ativo is not None:
        query = query.filter(models.Plano.ativo == ativo)

    return query.all()


@router.get("/planos/{plano_id}")
def get_plan_details(plano_id: int, db: Session = Depends(get_db)):
    """Detalhes de um plano incluindo estatísticas de uso"""
    plano = db.query(models.Plano).filter(models.Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    # Contar pedidos deste plano
    total_pedidos = db.query(func.count(models.Pedido.id)).filter(
        models.Pedido.plano_id == plano_id
    ).scalar()

    # Receita gerada por este plano
    receita = db.query(func.sum(models.Pedido.total)).filter(
        models.Pedido.plano_id == plano_id,
        models.Pedido.status.in_([
            models.StatusPedido.PAGAMENTO_APROVADO,
            models.StatusPedido.CONFIGURANDO_AMBIENTE,
            models.StatusPedido.INSTALANDO_AGENTE,
            models.StatusPedido.CONCLUIDO
        ])
    ).scalar() or 0

    return {
        "plano": plano,
        "total_pedidos": total_pedidos,
        "receita_gerada": receita
    }


@router.put("/planos/{plano_id}")
def update_plan(plano_id: int, updates: dict, db: Session = Depends(get_db)):
    """Atualizar um plano"""
    plano = db.query(models.Plano).filter(models.Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    # Atualizar campos permitidos
    allowed_fields = ["nome", "preco", "preco_antigo", "descricao", "recursos",
                      "link_pagamento", "destaque", "ativo"]

    for field, value in updates.items():
        if field in allowed_fields and hasattr(plano, field):
            setattr(plano, field, value)

    plano.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(plano)

    return plano


@router.post("/planos")
def create_plan(plano_data: dict, db: Session = Depends(get_db)):
    """Criar um novo plano"""
    novo_plano = models.Plano(**plano_data)
    db.add(novo_plano)
    db.commit()
    db.refresh(novo_plano)
    return novo_plano


@router.delete("/planos/{plano_id}")
def delete_plan(plano_id: int, db: Session = Depends(get_db)):
    """Desativar um plano (soft delete)"""
    plano = db.query(models.Plano).filter(models.Plano.id == plano_id).first()
    if not plano:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    # Verificar se há pedidos vinculados a este plano com clientes ativos
    pedidos_clientes_ativos = db.query(models.Pedido).join(
        models.Cliente, models.Pedido.cliente_id == models.Cliente.id
    ).filter(
        models.Pedido.plano_id == plano_id,
        models.Cliente.ativo == True
    ).count()

    if pedidos_clientes_ativos > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Não é possível excluir este plano. Existem {pedidos_clientes_ativos} pedido(s) vinculado(s) a cliente(s) ativo(s)."
        )

    # Verificar se há pedidos vinculados a este plano (clientes inativos)
    pedidos_count = db.query(func.count(models.Pedido.id)).filter(
        models.Pedido.plano_id == plano_id
    ).scalar()

    if pedidos_count > 0:
        # Se há pedidos (de clientes inativos), apenas desativa o plano
        plano.ativo = False
        plano.atualizado_em = datetime.utcnow()
        db.commit()
        return {"message": f"Plano desativado com sucesso ({pedidos_count} pedidos vinculados a clientes inativos)", "soft_delete": True}
    else:
        # Se não há pedidos, pode deletar permanentemente
        db.delete(plano)
        db.commit()
        return {"message": "Plano excluído permanentemente", "soft_delete": False}


# ============ GESTÃO DE PEDIDOS ============

@router.get("/pedidos")
def list_all_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    cliente_id: Optional[int] = None,
    plano_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar todos os pedidos com filtros"""
    query = db.query(models.Pedido)

    if status:
        query = query.filter(models.Pedido.status == status)

    if cliente_id:
        query = query.filter(models.Pedido.cliente_id == cliente_id)

    if plano_id:
        query = query.filter(models.Pedido.plano_id == plano_id)

    return query.order_by(desc(models.Pedido.criado_em)).offset(skip).limit(limit).all()


@router.get("/pedidos/{pedido_id}")
def get_order_details(pedido_id: int, db: Session = Depends(get_db)):
    """Detalhes completos de um pedido"""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    return {
        "pedido": pedido,
        "cliente": pedido.cliente,
        "plano": pedido.plano
    }


@router.put("/pedidos/{pedido_id}/status")
def update_order_status(pedido_id: int, novo_status: str, observacoes: Optional[str] = None, db: Session = Depends(get_db)):
    """Atualizar status de um pedido"""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Validar status
    try:
        status_enum = models.StatusPedido(novo_status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Status inválido")

    # Atualizar status
    pedido.status = status_enum
    pedido.atualizado_em = datetime.utcnow()
    if observacoes:
        pedido.observacoes = observacoes

    db.commit()
    db.refresh(pedido)

    return {"message": "Status atualizado com sucesso", "pedido": pedido}


@router.put("/pedidos/{pedido_id}")
def update_order(pedido_id: int, updates: dict, db: Session = Depends(get_db)):
    """Atualizar dados de um pedido"""
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Atualizar campos permitidos
    allowed_fields = ["metodo_pagamento", "gateway_id", "link_pagamento", "data_pagamento",
                      "valor", "desconto", "total", "observacoes", "configuracao_agente"]

    for field, value in updates.items():
        if field in allowed_fields and hasattr(pedido, field):
            setattr(pedido, field, value)

    pedido.atualizado_em = datetime.utcnow()
    db.commit()
    db.refresh(pedido)

    return pedido


# ============ VERIFICAÇÃO DE VENCIMENTOS ============

@router.get("/verificar-vencimentos")
def verificar_vencimentos(db: Session = Depends(get_db)):
    """
    Verifica pedidos vencidos e desativa clientes automaticamente.
    Retorna também pedidos que vão vencer em 10 dias (para notificar cliente).
    ESTE ENDPOINT DEVE SER EXECUTADO DIARIAMENTE via cron job ou agendador.
    """
    from datetime import date, timedelta

    hoje = date.today()
    data_limite_alerta = hoje + timedelta(days=10)  # Alertar 10 dias antes

    # Buscar pedidos vencidos (status ativo com data_validade passada)
    pedidos_vencidos = db.query(models.Pedido).join(
        models.Cliente
    ).filter(
        models.Pedido.status.in_([
            models.StatusPedido.PAGAMENTO_APROVADO,
            models.StatusPedido.CONCLUIDO
        ]),
        models.Cliente.ativo == True,
        models.Pedido.data_validade < hoje
    ).all()

    # Desativar clientes com pedidos vencidos
    clientes_desativados = []
    for pedido in pedidos_vencidos:
        if pedido.cliente.ativo:
            pedido.cliente.ativo = False
            pedido.status = models.StatusPedido.CANCELADO
            pedido.observacoes = (pedido.observacoes or '') + f"\n[{hoje}] Desativado automaticamente por vencimento."
            clientes_desativados.append({
                "cliente_id": pedido.cliente.id,
                "cliente_nome": pedido.cliente.nome,
                "pedido_id": pedido.id,
                "data_validade": pedido.data_validade.isoformat()
            })

    db.commit()

    # Buscar pedidos que vão vencer em 10 dias
    pedidos_a_vencer = db.query(models.Pedido).join(
        models.Cliente
    ).filter(
        models.Pedido.status.in_([
            models.StatusPedido.PAGAMENTO_APROVADO,
            models.StatusPedido.CONCLUIDO
        ]),
        models.Cliente.ativo == True,
        models.Pedido.data_validade.between(hoje, data_limite_alerta)
    ).all()

    alertas = []
    for pedido in pedidos_a_vencer:
        dias_restantes = (pedido.data_validade - hoje).days
        alertas.append({
            "pedido_id": pedido.id,
            "cliente_id": pedido.cliente.id,
            "cliente_nome": pedido.cliente.nome,
            "cliente_email": pedido.cliente.email,
            "plano_nome": pedido.plano.nome,
            "data_validade": pedido.data_validade.isoformat(),
            "dias_restantes": dias_restantes
        })

    return {
        "clientes_desativados": clientes_desativados,
        "total_desativados": len(clientes_desativados),
        "pedidos_a_vencer": alertas,
        "total_alertas": len(alertas)
    }


# ============ RENOVAÇÃO DE PLANO ============

@router.post("/pedidos/{pedido_id}/renovar")
def renovar_plano(pedido_id: int, db: Session = Depends(get_db)):
    """
    Cria um novo pedido de renovação do plano atual.
    O cliente deverá pagar novamente e ao confirmar pagamento via webhook,
    o sistema estenderá a validade do plano.
    """
    # Buscar pedido atual
    pedido_atual = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido_atual:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Verificar se cliente está ativo
    if not pedido_atual.cliente.ativo:
        raise HTTPException(
            status_code=400,
            detail="Cliente inativo. Entre em contato com o suporte."
        )

    # Criar novo pedido de renovação com mesmo plano
    novo_pedido = models.Pedido(
        cliente_id=pedido_atual.cliente_id,
        plano_id=pedido_atual.plano_id,
        valor=pedido_atual.plano.preco,
        desconto=0,
        total=pedido_atual.plano.preco,
        status=models.StatusPedido.AGUARDANDO_PAGAMENTO,
        link_pagamento=pedido_atual.plano.link_pagamento,
        observacoes=f"Renovação do pedido #{pedido_id}"
    )

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return {
        "message": "Pedido de renovação criado com sucesso",
        "pedido_renovacao": {
            "id": novo_pedido.id,
            "cliente_id": novo_pedido.cliente_id,
            "plano_id": novo_pedido.plano_id,
            "plano_nome": novo_pedido.plano.nome,
            "valor": novo_pedido.total,
            "status": novo_pedido.status.value,
            "link_pagamento": novo_pedido.link_pagamento,
            "criado_em": novo_pedido.criado_em.isoformat()
        },
        "pedido_anterior": {
            "id": pedido_atual.id,
            "data_inicio": pedido_atual.data_inicio.isoformat() if pedido_atual.data_inicio else None,
            "data_validade": pedido_atual.data_validade.isoformat() if pedido_atual.data_validade else None
        }
    }


# ============ RELATÓRIOS ============

@router.get("/relatorios/vendas")
def sales_report(
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Relatório de vendas por período"""
    query = db.query(models.Pedido).filter(
        models.Pedido.status.in_([
            models.StatusPedido.PAGAMENTO_APROVADO,
            models.StatusPedido.CONFIGURANDO_AMBIENTE,
            models.StatusPedido.INSTALANDO_AGENTE,
            models.StatusPedido.CONCLUIDO
        ])
    )

    if data_inicio:
        query = query.filter(models.Pedido.criado_em >= datetime.fromisoformat(data_inicio))

    if data_fim:
        query = query.filter(models.Pedido.criado_em <= datetime.fromisoformat(data_fim))

    pedidos = query.all()

    # Agrupar por plano
    vendas_por_plano = {}
    for pedido in pedidos:
        plano_nome = pedido.plano.nome
        if plano_nome not in vendas_por_plano:
            vendas_por_plano[plano_nome] = {
                "quantidade": 0,
                "receita": 0
            }
        vendas_por_plano[plano_nome]["quantidade"] += 1
        vendas_por_plano[plano_nome]["receita"] += pedido.total

    return {
        "total_vendas": len(pedidos),
        "receita_total": sum(p.total for p in pedidos),
        "vendas_por_plano": vendas_por_plano,
        "pedidos": pedidos
    }


# ============ CONFIGURAÇÕES DO SISTEMA ============

@router.get("/configuracoes-sistema", response_model=schemas.ConfiguracaoSistema)
def get_configuracoes_sistema(db: Session = Depends(get_db)):
    """Busca as configurações globais do sistema"""
    import crud
    return crud.get_configuracao_sistema(db)


@router.put("/configuracoes-sistema", response_model=schemas.ConfiguracaoSistema)
def update_configuracoes_sistema(
    configuracao: schemas.ConfiguracaoSistemaAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza as configurações globais do sistema"""
    import crud
    return crud.update_configuracao_sistema(db, configuracao)


# ============ TESTE DE CONEXÃO DOS SERVIÇOS ============

class TesteEvolutionRequest(BaseModel):
    url: str
    api_key: str

class TesteOllamaRequest(BaseModel):
    url: str
    model: str

class TesteQdrantRequest(BaseModel):
    url: str
    api_key: Optional[str] = None
    collection: str


@router.post("/testar-evolution")
def testar_evolution(dados: TesteEvolutionRequest):
    """Testa conexão com Evolution API"""
    import requests
    try:
        # Tenta buscar informações da instância ou listar instâncias
        response = requests.get(
            f"{dados.url.rstrip('/')}/instance/fetchInstances",
            headers={"apikey": dados.api_key},
            timeout=10
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Conexão estabelecida com sucesso!",
                "details": f"Status: {response.status_code}"
            }
        else:
            return {
                "success": False,
                "message": f"Falha na conexão. Status: {response.status_code}",
                "details": response.text[:200] if response.text else "Sem detalhes"
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Timeout: Evolution API não respondeu em 10 segundos",
            "details": "Verifique se a URL está correta e o serviço está rodando"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Erro de conexão: Não foi possível conectar ao Evolution API",
            "details": "Verifique se a URL está correta e o serviço está acessível"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro inesperado: {str(e)}",
            "details": "Verifique as configurações"
        }


@router.post("/testar-ollama")
def testar_ollama(dados: TesteOllamaRequest):
    """Testa conexão com Ollama"""
    import requests
    try:
        # Tenta listar modelos disponíveis
        response = requests.get(
            f"{dados.url.rstrip('/')}/api/tags",
            timeout=10
        )

        if response.status_code == 200:
            models_data = response.json()
            models = [m.get('name', 'unknown') for m in models_data.get('models', [])]

            # Verificar se o modelo configurado existe
            model_exists = any(dados.model in m for m in models)

            if model_exists:
                return {
                    "success": True,
                    "message": f"Conexão OK! Modelo '{dados.model}' encontrado.",
                    "details": f"Modelos disponíveis: {', '.join(models[:5])}"
                }
            else:
                return {
                    "success": False,
                    "message": f"Conexão OK, mas modelo '{dados.model}' não encontrado",
                    "details": f"Modelos disponíveis: {', '.join(models) if models else 'Nenhum'}"
                }
        else:
            return {
                "success": False,
                "message": f"Falha na conexão. Status: {response.status_code}",
                "details": "Verifique se o Ollama está rodando"
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Timeout: Ollama não respondeu em 10 segundos",
            "details": "Verifique se o serviço está rodando e acessível"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Erro de conexão: Não foi possível conectar ao Ollama",
            "details": "Verifique se a URL está correta e o serviço está rodando"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro inesperado: {str(e)}",
            "details": "Verifique as configurações"
        }


@router.post("/testar-qdrant")
def testar_qdrant(dados: TesteQdrantRequest):
    """Testa conexão com Qdrant"""
    import requests
    try:
        headers = {}
        if dados.api_key:
            headers["api-key"] = dados.api_key

        # Tenta listar coleções
        response = requests.get(
            f"{dados.url.rstrip('/')}/collections",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            collections_data = response.json()
            collections = [c.get('name') for c in collections_data.get('result', {}).get('collections', [])]

            # Verificar se a coleção configurada existe
            collection_exists = dados.collection in collections

            if collection_exists:
                return {
                    "success": True,
                    "message": f"Conexão OK! Coleção '{dados.collection}' encontrada.",
                    "details": f"Coleções disponíveis: {', '.join(collections)}"
                }
            else:
                return {
                    "success": True,
                    "message": f"Conexão OK, mas coleção '{dados.collection}' não existe",
                    "details": f"Será criada automaticamente. Coleções existentes: {', '.join(collections) if collections else 'Nenhuma'}"
                }
        else:
            return {
                "success": False,
                "message": f"Falha na conexão. Status: {response.status_code}",
                "details": "Verifique se o Qdrant está rodando e as credenciais"
            }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Timeout: Qdrant não respondeu em 10 segundos",
            "details": "Verifique se o serviço está rodando"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Erro de conexão: Não foi possível conectar ao Qdrant",
            "details": "Verifique se a URL está correta e o serviço está rodando"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro inesperado: {str(e)}",
            "details": "Verifique as configurações"
        }
