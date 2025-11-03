from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import crud
import schemas
import models
from database import get_db
from datetime import date, timedelta
import hashlib

router = APIRouter(prefix="/api/clients", tags=["Clients"])


# ============ AUTENTICAÇÃO CLIENTE ============

class ClientLoginRequest(BaseModel):
    email: str
    senha: str


class ClientLoginResponse(BaseModel):
    cliente_id: int
    nome: str
    email: str
    ativo: bool


@router.post("/login", response_model=ClientLoginResponse)
def client_login(
    credentials: ClientLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Autentica um cliente"""

    # Buscar cliente por email
    client = db.query(models.Cliente).filter(
        models.Cliente.email == credentials.email
    ).first()

    if not client:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

    # Verificar senha (bcrypt)
    import bcrypt
    senha_correta = bcrypt.checkpw(
        credentials.senha.encode('utf-8'),
        client.senha_hash.encode('utf-8')
    )

    if not senha_correta:
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )

    # Setar cookie com o client_id para o painel poder acessar
    response.set_cookie(
        key="client_id",
        value=str(client.id),
        max_age=30*24*60*60,  # 30 dias
        httponly=True,
        samesite="lax"
    )

    return ClientLoginResponse(
        cliente_id=client.id,
        nome=client.nome,
        email=client.email,
        ativo=client.ativo
    )


# ============ ENDPOINTS PARA O PAINEL (COOKIE-BASED) ============

@router.get("/me", response_model=schemas.Cliente)
def get_current_client(
    client_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Busca dados do cliente logado via cookie"""
    if not client_id:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        client_id_int = int(client_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Cookie inválido")

    client = crud.get_client(db, client_id_int)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return client


@router.put("/me", response_model=schemas.Cliente)
def update_current_client(
    client_update: schemas.ClienteAtualizar,
    client_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Atualiza dados do cliente logado via cookie"""
    if not client_id:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        client_id_int = int(client_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Cookie inválido")

    updated_client = crud.update_client(db, client_id_int, client_update)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return updated_client


@router.post("/change-password")
def change_current_client_password(
    password_data: dict,
    client_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Altera senha do cliente logado via cookie"""
    if not client_id:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        client_id_int = int(client_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Cookie inválido")

    import bcrypt

    client = crud.get_client(db, client_id_int)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Obter senhas do payload
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")

    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Senha atual e nova senha são obrigatórias"
        )

    # Verificar senha atual
    if not bcrypt.checkpw(
        current_password.encode('utf-8'),
        client.senha_hash.encode('utf-8')
    ):
        raise HTTPException(status_code=401, detail="Senha atual incorreta")

    # Validar nova senha
    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="A nova senha deve ter no mínimo 6 caracteres"
        )

    # Gerar hash da nova senha
    new_password_hash = bcrypt.hashpw(
        new_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')

    # Atualizar senha no banco
    client.senha_hash = new_password_hash
    db.commit()

    return {"message": "Senha alterada com sucesso"}


@router.post("/logout")
def logout_client(response: Response):
    """Faz logout do cliente limpando o cookie"""
    # Remover cookie
    response.delete_cookie(key="client_id")
    return {"message": "Logout realizado com sucesso"}


@router.get("/", response_model=List[schemas.Cliente])
def list_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os clientes"""
    clients = crud.get_clients(db, skip=skip, limit=limit)
    return clients


@router.get("/{client_id}", response_model=schemas.Cliente)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Busca um cliente específico"""
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.get("/email/{email}", response_model=schemas.Cliente)
def get_client_by_email(email: str, db: Session = Depends(get_db)):
    """Busca cliente por email"""
    client = crud.get_client_by_email(db, email)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.post("/", response_model=schemas.Cliente)
def create_client(client: schemas.ClienteCriar, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    # Verificar se email já existe
    existing_client = crud.get_client_by_email(db, client.email)
    if existing_client:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    return crud.create_client(db, client)


@router.put("/{client_id}", response_model=schemas.Cliente)
def update_client(
    client_id: int,
    client: schemas.ClienteAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza dados do cliente"""
    updated_client = crud.update_client(db, client_id, client)
    if not updated_client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return updated_client


@router.get("/{client_id}/dashboard")
def get_client_dashboard(client_id: int, db: Session = Depends(get_db)):
    """Retorna todos os dados para o dashboard do cliente"""
    from sqlalchemy import func, desc

    # Verificar se cliente existe
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar todos os pedidos do cliente
    pedidos = db.query(models.Pedido).filter(
        models.Pedido.cliente_id == client_id
    ).order_by(desc(models.Pedido.criado_em)).all()

    # Buscar pedido ativo (com validade válida)
    hoje = date.today()
    pedido_ativo = None
    dias_restantes = None
    alerta_vencimento = False

    for pedido in pedidos:
        if pedido.data_validade and pedido.data_validade >= hoje and pedido.cliente.ativo:
            pedido_ativo = pedido
            dias_restantes = (pedido.data_validade - hoje).days
            alerta_vencimento = dias_restantes <= 10
            break

    # Total de conversas
    total_conversas = 0
    total_mensagens = 0

    if pedidos:
        pedido_ids = [p.id for p in pedidos]
        total_conversas = db.query(func.count(models.Conversa.id)).filter(
            models.Conversa.pedido_id.in_(pedido_ids)
        ).scalar() or 0

        total_mensagens = db.query(func.count(models.Mensagem.id)).join(
            models.Conversa
        ).filter(
            models.Conversa.pedido_id.in_(pedido_ids)
        ).scalar() or 0

    # Formatar pedidos para resposta
    pedidos_list = []
    for p in pedidos:
        pedidos_list.append({
            "id": p.id,
            "plano": {
                "nome": p.plano.nome,
                "tipo": p.plano.tipo.value,
                "periodo": p.plano.periodo.value
            } if p.plano else None,
            "status": p.status.value,
            "data_inicio": p.data_inicio.isoformat() if p.data_inicio else None,
            "data_validade": p.data_validade.isoformat() if p.data_validade else None,
            "total": p.total,
            "link_pagamento": p.link_pagamento,
            "criado_em": p.criado_em.isoformat()
        })

    return {
        "cliente": {
            "id": client.id,
            "nome": client.nome,
            "email": client.email,
            "whatsapp": client.whatsapp,
            "ativo": client.ativo
        },
        "pedido_ativo": {
            "id": pedido_ativo.id,
            "plano": {
                "nome": pedido_ativo.plano.nome,
                "tipo": pedido_ativo.plano.tipo.value,
                "periodo": pedido_ativo.plano.periodo.value
            },
            "data_inicio": pedido_ativo.data_inicio.isoformat() if pedido_ativo.data_inicio else None,
            "data_validade": pedido_ativo.data_validade.isoformat() if pedido_ativo.data_validade else None,
            "dias_restantes": dias_restantes
        } if pedido_ativo else None,
        "alerta_vencimento": alerta_vencimento,
        "dias_restantes": dias_restantes,
        "pedidos": pedidos_list,
        "metricas": {
            "total_conversas": total_conversas,
            "total_mensagens": total_mensagens
        }
    }


@router.get("/{client_id}/metrics")
def get_client_metrics(client_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Busca métricas dos últimos N dias do cliente"""
    # Verificar se cliente existe
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Buscar pedidos do cliente
    pedidos = db.query(models.Pedido).filter(
        models.Pedido.cliente_id == client_id
    ).all()

    if not pedidos:
        # Cliente sem pedidos, retornar vazio
        return {
            "labels": [],
            "mensagens": [],
            "contatos": [],
            "conversas": []
        }

    pedido_ids = [p.id for p in pedidos]

    # Buscar métricas dos últimos N dias
    data_inicio = date.today() - timedelta(days=days - 1)

    metricas = db.query(models.MetricaDiaria).filter(
        models.MetricaDiaria.pedido_id.in_(pedido_ids),
        models.MetricaDiaria.data >= data_inicio
    ).order_by(models.MetricaDiaria.data).all()

    # Formatar resposta (agregando por data se houver múltiplos pedidos)
    resultado = {
        "labels": [],
        "mensagens": [],
        "contatos": [],
        "conversas": []
    }

    # Agrupar por data
    from collections import defaultdict
    metricas_por_data = defaultdict(lambda: {"mensagens": 0, "contatos": 0, "conversas": 0})

    for metrica in metricas:
        data_str = metrica.data.strftime("%d/%m")
        metricas_por_data[metrica.data]["mensagens"] += metrica.total_mensagens
        metricas_por_data[metrica.data]["contatos"] += metrica.total_contatos
        metricas_por_data[metrica.data]["conversas"] += metrica.conversas_iniciadas

    # Ordenar por data e formatar
    for data in sorted(metricas_por_data.keys()):
        resultado["labels"].append(data.strftime("%d/%m"))
        resultado["mensagens"].append(metricas_por_data[data]["mensagens"])
        resultado["contatos"].append(metricas_por_data[data]["contatos"])
        resultado["conversas"].append(metricas_por_data[data]["conversas"])

    return resultado


@router.post("/{client_id}/change-password")
def change_password(
    client_id: int,
    password_data: dict,
    db: Session = Depends(get_db)
):
    """Altera a senha do cliente"""
    import bcrypt

    # Verificar se cliente existe
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    # Obter senhas do payload
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")

    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Senha atual e nova senha são obrigatórias")

    # Verificar senha atual
    if not bcrypt.checkpw(current_password.encode('utf-8'), client.senha_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Senha atual incorreta")

    # Validar nova senha (mínimo 6 caracteres)
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="A nova senha deve ter no mínimo 6 caracteres")

    # Gerar hash da nova senha
    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Atualizar senha no banco
    client.senha_hash = new_password_hash
    db.commit()

    return {"message": "Senha alterada com sucesso"}
