from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import crud
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class LoginResponse(BaseModel):
    client_id: int
    nome: str
    email: str
    order_id: int = None
    agent_type: str = None
    plan_name: str = None


@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Autentica um cliente usando email e senha.
    Retorna os dados do cliente e do pedido mais recente para redirecionamento ao painel.
    """
    # Buscar cliente por email
    client = crud.get_client_by_email(db, credentials.email)

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Cliente não encontrado. Verifique seu email."
        )

    # Verificar se cliente está ativo
    if not client.ativo:
        raise HTTPException(
            status_code=403,
            detail="Cliente desativado. Entre em contato com o suporte."
        )

    # Verificar senha usando bcrypt
    import bcrypt

    if not client.senha_hash:
        raise HTTPException(
            status_code=401,
            detail="Senha não configurada para este usuário."
        )

    try:
        senha_correta = bcrypt.checkpw(
            credentials.senha.encode('utf-8'),
            client.senha_hash.encode('utf-8')
        )

        if not senha_correta:
            raise HTTPException(
                status_code=401,
                detail="Senha incorreta."
            )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Erro ao verificar senha."
        )

    # Buscar pedido mais recente do cliente
    orders = crud.get_orders_by_client(db, client.id)

    order_data = {}
    if orders and len(orders) > 0:
        # Pegar o pedido mais recente
        most_recent_order = orders[0]

        # Buscar dados do plano
        plan = crud.get_plan(db, most_recent_order.plano_id)

        if plan:
            order_data = {
                "order_id": most_recent_order.id,
                "agent_type": plan.tipo,
                "plan_name": plan.nome
            }

    return LoginResponse(
        client_id=client.id,
        nome=client.nome,
        email=client.email,
        **order_data
    )
