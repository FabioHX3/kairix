from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
import models
from database import get_db

router = APIRouter(prefix="/api/plans", tags=["Plans"])


@router.get("/", response_model=List[schemas.Plano])
def list_plans(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = None,
    db: Session = Depends(get_db)
):
    """Lista todos os planos"""
    plans = crud.get_plans(db, skip=skip, limit=limit, is_active=is_active)
    return plans


@router.get("/type/{plan_type}", response_model=List[schemas.Plano])
def get_plans_by_type(
    plan_type: models.TipoPlano,
    db: Session = Depends(get_db)
):
    """Busca planos por tipo (bot_normal, bot_ia, agente_financeiro)"""
    plans = crud.get_plans_by_type(db, plan_type)
    return plans


@router.get("/{plan_id}", response_model=schemas.Plano)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Busca um plano específico"""
    plan = crud.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return plan


@router.post("/", response_model=schemas.Plano)
def create_plan(plan: schemas.PlanoCriar, db: Session = Depends(get_db)):
    """Cria um novo plano"""
    return crud.create_plan(db, plan)


@router.put("/{plan_id}", response_model=schemas.Plano)
def update_plan(
    plan_id: int,
    plan: schemas.PlanoAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza um plano existente"""
    updated_plan = crud.update_plan(db, plan_id, plan)
    if not updated_plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return updated_plan


@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """Deleta um plano"""
    success = crud.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plano não encontrado")
    return {"message": "Plano deletado com sucesso"}
