from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta
import crud
import schemas
import models
from database import get_db

router = APIRouter(prefix="/api/conversas", tags=["Conversas"])


@router.get("/pedido/{pedido_id}", response_model=List[schemas.Conversa])
def listar_conversas_pedido(
    pedido_id: int,
    skip: int = 0,
    limit: int = 100,
    data_inicio: date = None,
    data_fim: date = None,
    db: Session = Depends(get_db)
):
    """Lista todas as conversas de um pedido, com filtros opcionais de data"""
    conversas = crud.get_conversas_by_pedido(db, pedido_id, skip, limit, data_inicio, data_fim)
    return conversas


@router.get("/{conversa_id}", response_model=schemas.ConversaComMensagens)
def get_conversa_detalhes(conversa_id: int, db: Session = Depends(get_db)):
    """Busca detalhes de uma conversa com suas mensagens"""
    conversa = crud.get_conversa(db, conversa_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conversa


@router.post("/", response_model=schemas.Conversa)
def criar_conversa(conversa: schemas.ConversaCriar, db: Session = Depends(get_db)):
    """Cria uma nova conversa"""
    # Verificar se já existe conversa ativa para este contato
    conversa_existente = crud.get_conversa_by_numero(
        db, conversa.pedido_id, conversa.contato_numero
    )
    if conversa_existente:
        return conversa_existente

    return crud.create_conversa(db, conversa)


@router.put("/{conversa_id}", response_model=schemas.Conversa)
def atualizar_conversa(
    conversa_id: int,
    conversa: schemas.ConversaAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza dados de uma conversa"""
    db_conversa = crud.update_conversa(db, conversa_id, conversa)
    if not db_conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return db_conversa


@router.get("/{conversa_id}/mensagens", response_model=List[schemas.Mensagem])
def listar_mensagens(
    conversa_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista mensagens de uma conversa"""
    mensagens = crud.get_mensagens_by_conversa(db, conversa_id, skip, limit)
    return mensagens


@router.post("/mensagens", response_model=schemas.Mensagem)
def criar_mensagem(mensagem: schemas.MensagemCriar, db: Session = Depends(get_db)):
    """Cria uma nova mensagem"""
    # Verificar se conversa existe
    conversa = crud.get_conversa(db, mensagem.conversa_id)
    if not conversa:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    return crud.create_mensagem(db, mensagem)


@router.put("/mensagens/{mensagem_id}", response_model=schemas.Mensagem)
def atualizar_mensagem(
    mensagem_id: int,
    mensagem: schemas.MensagemAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza uma mensagem"""
    db_mensagem = crud.update_mensagem(db, mensagem_id, mensagem)
    if not db_mensagem:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")
    return db_mensagem


# ============= MÉTRICAS =============

@router.get("/metricas/{pedido_id}", response_model=List[schemas.MetricaDiaria])
def get_metricas(
    pedido_id: int,
    data_inicio: date = None,
    data_fim: date = None,
    db: Session = Depends(get_db)
):
    """Busca métricas de um período"""
    if not data_inicio:
        data_inicio = date.today() - timedelta(days=30)
    if not data_fim:
        data_fim = date.today()

    return crud.get_metricas_periodo(db, pedido_id, data_inicio, data_fim)


@router.post("/metricas/{pedido_id}/calcular")
def calcular_metricas(
    pedido_id: int,
    data_calculo: date = None,
    db: Session = Depends(get_db)
):
    """Calcula métricas para uma data específica"""
    if not data_calculo:
        data_calculo = date.today()

    metrica = crud.calcular_metricas_diarias(db, pedido_id, data_calculo)

    return {
        "message": "Métricas calculadas com sucesso",
        "metrica": metrica
    }
