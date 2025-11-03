from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import schemas
import models
from database import get_db
import os

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# URL base do gateway de pagamento (pode ser configurada no .env)
PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "https://pay.kiwify.com.br")


@router.get("/", response_model=List[schemas.Pedido])
def list_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lista todos os pedidos"""
    orders = crud.get_orders(db, skip=skip, limit=limit)
    return orders


@router.get("/me", response_model=List[schemas.Pedido])
def get_current_client_orders(
    client_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """Lista pedidos do cliente logado via cookie"""
    if not client_id:
        raise HTTPException(status_code=401, detail="Não autenticado")

    try:
        client_id_int = int(client_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Cookie inválido")

    orders = crud.get_orders_by_client(db, client_id_int)
    return orders


@router.get("/client/{client_id}", response_model=List[schemas.Pedido])
def get_client_orders(client_id: int, db: Session = Depends(get_db)):
    """Lista pedidos de um cliente"""
    orders = crud.get_orders_by_client(db, client_id)
    return orders


@router.get("/status/{status}", response_model=List[schemas.Pedido])
def get_orders_by_status(
    status: models.StatusPedido,
    db: Session = Depends(get_db)
):
    """Lista pedidos por status"""
    orders = crud.get_orders_by_status(db, status)
    return orders


@router.get("/{order_id}", response_model=schemas.PedidoComDetalhes)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Busca um pedido específico com detalhes"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.post("/register", response_model=schemas.RespostaRegistro)
def register_client_with_plan(
    registration: schemas.RegistroCliente,
    db: Session = Depends(get_db)
):
    """
    Registra um novo cliente com um plano selecionado.
    Retorna os dados do cliente, pedido e link de pagamento.
    """
    # Verificar se o plano existe
    plan = crud.get_plan(db, registration.plano_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano não encontrado")

    # Verificar se email já existe
    existing_client = crud.get_client_by_email(db, registration.cliente.email)
    if existing_client:
        # Cliente já existe, usar o existente
        client = existing_client
    else:
        # Criar novo cliente
        client = crud.create_client(db, registration.cliente)

    # Criar pedido
    order_data = schemas.OrderCreate(
        cliente_id=client.id,
        plano_id=plan.id,
        valor=plan.preco,
        desconto=0,
        total=plan.preco
    )
    order = crud.create_order(db, order_data)

    # Usar o link de pagamento cadastrado no plano
    payment_link = plan.link_pagamento or f"{PAYMENT_GATEWAY_URL}/seu-link-{plan.tipo.value}-{plan.periodo.value}"

    # Atualizar pedido com link de pagamento
    order_update = schemas.OrderUpdate(
        link_pagamento=payment_link,
        status=models.StatusPedido.AGUARDANDO_PAGAMENTO
    )
    order = crud.update_order(db, order.id, order_update)

    return schemas.RegistrationResponse(
        cliente=client,
        pedido=order,
        link_pagamento=payment_link
    )


@router.put("/{order_id}/status", response_model=schemas.Pedido)
def update_order_status(
    order_id: int,
    status_update: schemas.PedidoStatusAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza o status do pedido"""
    order = crud.update_order_status(db, order_id, status_update)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.put("/{order_id}", response_model=schemas.Pedido)
def update_order(
    order_id: int,
    order_update: schemas.PedidoAtualizar,
    db: Session = Depends(get_db)
):
    """Atualiza dados do pedido"""
    order = crud.update_order(db, order_id, order_update)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return order


@router.post("/{order_id}/confirm-payment", response_model=schemas.Pedido)
def confirm_payment(
    order_id: int,
    payment_data: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook para confirmar pagamento.
    Deve ser chamado pelo gateway de pagamento após confirmação.
    """
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Atualizar status e dados do pagamento
    from datetime import datetime
    order_update = schemas.OrderUpdate(
        status=models.StatusPedido.PAGAMENTO_APROVADO,
        metodo_pagamento=payment_data.get("payment_method"),
        gateway_id=payment_data.get("transaction_id"),
        data_pagamento=datetime.utcnow(),
        observacoes="Pagamento confirmado pelo gateway"
    )

    order = crud.update_order(db, order_id, order_update)
    return order


@router.post("/webhook/kirvano")
async def kirvano_webhook(webhook_data: dict, db: Session = Depends(get_db)):
    """
    Webhook da Kirvano para notificar pagamento aprovado.
    Ativa o cliente e gera configurações modelo.
    """
    from datetime import datetime
    import json

    # Extrair dados do webhook da Kirvano
    # Suporta múltiplos formatos de dados
    transaction_id = webhook_data.get("transaction_id") or webhook_data.get("id")
    payment_status = webhook_data.get("status")

    # Tentar pegar email de diferentes lugares
    customer_email = None
    if isinstance(webhook_data.get("customer"), dict):
        customer_email = webhook_data["customer"].get("email")
    else:
        customer_email = webhook_data.get("email") or webhook_data.get("customer_email")

    # Tentar pegar custom fields/metadata da Kirvano
    metadata = webhook_data.get("metadata") or webhook_data.get("custom_fields") or {}
    order_id_metadata = metadata.get("order_id") or webhook_data.get("order_id")

    # Verificar se é pagamento aprovado
    if payment_status not in ["approved", "paid", "completed"]:
        return {"status": "ignored", "message": "Payment not approved yet"}

    # Buscar pedido por prioridade
    order = None

    # 1. Tentar por order_id dos custom fields (MAIS CONFIÁVEL)
    if order_id_metadata:
        try:
            order = db.query(models.Pedido).filter(models.Pedido.id == int(order_id_metadata)).first()
        except (ValueError, TypeError):
            pass

    # 2. Tentar por transaction_id já salvo
    if not order and transaction_id:
        order = db.query(models.Pedido).filter(models.Pedido.gateway_id == transaction_id).first()

    # 3. Tentar por email do cliente (pedido mais recente aguardando)
    if not order and customer_email:
        client = crud.get_client_by_email(db, customer_email)
        if client:
            order = db.query(models.Pedido).filter(
                models.Pedido.cliente_id == client.id,
                models.Pedido.status == models.StatusPedido.AGUARDANDO_PAGAMENTO
            ).order_by(models.Pedido.criado_em.desc()).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail=f"Pedido não encontrado. Email: {customer_email}, Transaction: {transaction_id}, Order ID: {order_id_metadata}"
        )

    # Calcular data de início (data do pagamento) e data de validade
    data_inicio = datetime.utcnow().date()

    # Calcular validade baseada no período do plano
    # Mensal: 30 dias, Semestral: 180 dias, Anual: 365 dias
    if order.plano.periodo == models.PeriodoPlano.MENSAL:
        data_validade = data_inicio + timedelta(days=30)
    elif order.plano.periodo == models.PeriodoPlano.SEMESTRAL:
        data_validade = data_inicio + timedelta(days=180)
    elif order.plano.periodo == models.PeriodoPlano.ANUAL:
        data_validade = data_inicio + timedelta(days=365)
    else:
        data_validade = data_inicio + timedelta(days=30)  # Default mensal

    # Atualizar pedido
    order.status = models.StatusPedido.PAGAMENTO_APROVADO
    order.gateway_id = transaction_id
    order.data_pagamento = datetime.utcnow()
    order.data_inicio = data_inicio  # Data de início do plano
    order.data_validade = data_validade  # Data de vencimento
    order.metodo_pagamento = webhook_data.get("payment_method", "card")

    # Ativar cliente
    client = order.cliente
    client.ativo = True

    # Criar configuração do bot se não existir
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == order.id
    ).first()

    if not config:
        # Respostas rápidas modelo
        respostas_modelo = [
            {
                "palavras_chave": ["horário", "horario", "hora", "atendimento"],
                "resposta": "🕐 Nosso horário de atendimento é de segunda a sexta, das 9h às 18h."
            },
            {
                "palavras_chave": ["endereço", "endereco", "onde", "localização", "localizacao"],
                "resposta": "📍 Estamos localizados em [SEU ENDEREÇO AQUI]."
            },
            {
                "palavras_chave": ["preço", "preco", "valor", "quanto custa"],
                "resposta": "💰 Entre em contato conosco para solicitar um orçamento personalizado!"
            }
        ]

        # Menu interativo modelo (1 nível)
        menu_modelo = [
            {
                "numero": "1",
                "titulo": "📞 Falar com Atendente",
                "descricao": "Ser direcionado para um de nossos atendentes",
                "acao": "atendente"
            },
            {
                "numero": "2",
                "titulo": "ℹ️ Informações",
                "descricao": "Horários, endereço e contatos",
                "acao": "informacoes"
            },
            {
                "numero": "3",
                "titulo": "💼 Serviços",
                "descricao": "Conheça nossos produtos e serviços",
                "acao": "servicos"
            }
        ]

        # Criar configuração
        config = models.ConfiguracaoBot(
            pedido_id=order.id,
            mensagem_boas_vindas="👋 Olá! Seja bem-vindo(a)!\n\nComo posso ajudá-lo(a) hoje?",
            mensagem_nao_entendida="Desculpe, não entendi sua mensagem. Por favor, escolha uma das opções do menu ou reformule sua pergunta.",
            respostas_rapidas=json.dumps(respostas_modelo, ensure_ascii=False),
            menu_interativo=json.dumps(menu_modelo, ensure_ascii=False),
            timeout_inatividade=300,
            ativo=True
        )
        db.add(config)
        db.flush()  # Salvar config antes de criar instância

    # Criar instância no Evolution API automaticamente
    import evolution_helper
    evolution_result = None
    try:
        # Importar asyncio para rodar função async
        import asyncio
        evolution_result = asyncio.run(evolution_helper.criar_instancia_evolution(db, client, order))

        if evolution_result and evolution_result.get("success"):
            print(f"✅ Instância Evolution criada: {evolution_result.get('instance_name')}")
        else:
            print(f"⚠️ Falha ao criar instância Evolution: {evolution_result.get('error') if evolution_result else 'Erro desconhecido'}")
    except Exception as e:
        print(f"❌ Exceção ao criar instância Evolution: {str(e)}")

    db.commit()
    db.refresh(order)

    response_data = {
        "status": "success",
        "message": "Payment processed successfully",
        "order_id": order.id,
        "client_activated": True,
        "config_created": True
    }

    # Adicionar informações da instância Evolution se foi criada
    if evolution_result and evolution_result.get("success"):
        response_data["evolution_instance"] = {
            "created": True,
            "instance_name": evolution_result.get("instance_name"),
            "numero": evolution_result.get("numero"),
            "qrcode_available": evolution_result.get("qrcode") is not None
        }
    else:
        response_data["evolution_instance"] = {
            "created": False,
            "error": evolution_result.get("error") if evolution_result else "Não foi possível criar instância"
        }

    return response_data
