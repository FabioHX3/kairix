from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import crud
import models
from database import get_db
from schemas_config import ConfiguracaoResponse, ConfiguracaoUpdate
from pydantic import BaseModel

router = APIRouter(prefix="/api/config", tags=["Configuration"])


# ========== SCHEMAS ==========
class RespostaPredefinida(BaseModel):
    id: int = None
    pergunta: str
    resposta: str
    palavras_chave: List[str] = []


class SubOpcao(BaseModel):
    numero: str
    titulo: str
    resposta: str = None


class OpcaoMenu(BaseModel):
    id: int = None
    numero: str
    titulo: str
    descricao: str = None
    acao: str  # 'resposta', 'submenu', 'atendente'
    resposta: str = None  # Se acao == 'resposta'
    submenu: str = None  # JSON string das sub-opções se acao == 'submenu'


class FluxoConversa(BaseModel):
    id: int = None
    nome: str
    descricao: str = None
    etapas: List[dict] = []


class Integracao(BaseModel):
    id: int = None
    tipo: str  # 'crm', 'gateway_pagamento', 'erp'
    nome: str
    webhook_url: str = None
    api_key: str = None
    documentacao: str = None  # URL ou texto
    ativo: bool = True


@router.get("/{order_id}", response_model=ConfiguracaoResponse)
def get_order_configuration(order_id: int, db: Session = Depends(get_db)):
    """
    Retorna a configuração do agente para um pedido específico.
    """
    order = crud.get_order(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar plano para saber o tipo
    plan = crud.get_plan(db, order.plano_id)

    configuracao = {}
    configurado = False

    if order.configuracao_agente:
        try:
            configuracao = json.loads(order.configuracao_agente)
            configurado = True
        except json.JSONDecodeError:
            configuracao = {}

    return ConfiguracaoResponse(
        pedido_id=order.id,
        tipo_agente=plan.tipo.value,
        configuracao=configuracao,
        configurado=configurado,
        ultima_atualizacao=str(order.atualizado_em) if order.atualizado_em else None
    )


@router.put("/{order_id}")
def update_order_configuration(
    order_id: int,
    config_update: ConfiguracaoUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza a configuração do agente para um pedido específico.
    """
    order = crud.get_order(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Verificar se o pagamento foi aprovado
    if order.status not in [models.StatusPedido.PAGAMENTO_APROVADO,
                             models.StatusPedido.CONFIGURANDO_AMBIENTE,
                             models.StatusPedido.INSTALANDO_AGENTE,
                             models.StatusPedido.CONCLUIDO]:
        raise HTTPException(
            status_code=400,
            detail="Configuração disponível apenas após aprovação do pagamento"
        )

    # Salvar configuração como JSON
    order.configuracao_agente = json.dumps(config_update.configuracao, ensure_ascii=False)

    # Se estava em PAGAMENTO_APROVADO, mudar para CONFIGURANDO_AMBIENTE
    if order.status == models.StatusPedido.PAGAMENTO_APROVADO:
        from datetime import datetime
        from schemas import OrderStatusUpdate

        status_update = OrderStatusUpdate(
            status=models.StatusPedido.CONFIGURANDO_AMBIENTE,
            observacoes="Cliente iniciou configuração do agente"
        )
        order = crud.update_order_status(db, order_id, status_update)
    else:
        db.commit()
        db.refresh(order)

    return {"message": "Configuração atualizada com sucesso", "pedido_id": order.id}


@router.get("/{order_id}/template")
def get_configuration_template(order_id: int, db: Session = Depends(get_db)):
    """
    Retorna um template de configuração baseado no tipo de produto e plano.
    """
    order = crud.get_order(db, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    plan = crud.get_plan(db, order.plano_id)

    # Templates baseados no tipo de agente e no plano
    templates = {
        "agente_normal": {
            "Starter": {
                "limite_respostas": 50,
                "integracao_crm": False,
                "customizacoes_avancadas": False
            },
            "Professional": {
                "limite_respostas": 100,
                "integracao_crm": True,
                "customizacoes_avancadas": True
            },
            "Enterprise": {
                "limite_respostas": None,  # Ilimitado
                "integracao_crm": True,
                "customizacoes_avancadas": True,
                "api_access": True
            }
        },
        "agente_ia": {
            "IA Essencial": {
                "limite_mb": 100,
                "limite_interacoes_mes": 1000,
                "fine_tuning": False
            },
            "IA Professional": {
                "limite_mb": 500,
                "limite_interacoes_mes": 5000,
                "fine_tuning": False
            },
            "IA Enterprise": {
                "limite_mb": None,  # Ilimitado
                "limite_interacoes_mes": None,  # Ilimitado
                "fine_tuning": True
            }
        },
        "agente_financeiro": {
            "Starter": {
                "limite_transacoes": 100,
                "integracao_gateway": False
            },
            "Professional": {
                "limite_transacoes": 500,
                "integracao_gateway": True
            },
            "Enterprise": {
                "limite_transacoes": None,  # Ilimitado
                "integracao_gateway": True,
                "api_access": True
            }
        }
    }

    tipo_agente = plan.tipo.value
    nome_plano = plan.nome

    template = templates.get(tipo_agente, {}).get(nome_plano, {})

    return {
        "tipo_agente": tipo_agente,
        "plano": nome_plano,
        "template": template
    }


# ========== RESPOSTAS PREDEFINIDAS ==========
@router.get("/{order_id}/respostas", response_model=List[RespostaPredefinida])
def get_respostas(order_id: int, db: Session = Depends(get_db)):
    """Retorna todas as respostas predefinidas do pedido"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}
    return config.get("respostas", [])


@router.post("/{order_id}/respostas")
def add_resposta(order_id: int, resposta: RespostaPredefinida, db: Session = Depends(get_db)):
    """Adiciona uma nova resposta predefinida"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    if "respostas" not in config:
        config["respostas"] = []

    # Gerar ID
    novo_id = max([r.get("id", 0) for r in config["respostas"]], default=0) + 1
    resposta_dict = resposta.dict()
    resposta_dict["id"] = novo_id

    config["respostas"].append(resposta_dict)
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Resposta adicionada", "id": novo_id}


@router.put("/{order_id}/respostas/{resposta_id}")
def update_resposta(order_id: int, resposta_id: int, resposta: RespostaPredefinida, db: Session = Depends(get_db)):
    """Atualiza uma resposta predefinida"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    respostas = config.get("respostas", [])
    for i, r in enumerate(respostas):
        if r.get("id") == resposta_id:
            resposta_dict = resposta.dict()
            resposta_dict["id"] = resposta_id
            respostas[i] = resposta_dict
            config["respostas"] = respostas
            order.configuracao_agente = json.dumps(config, ensure_ascii=False)
            db.commit()
            return {"message": "Resposta atualizada"}

    raise HTTPException(status_code=404, detail="Resposta não encontrada")


@router.delete("/{order_id}/respostas/{resposta_id}")
def delete_resposta(order_id: int, resposta_id: int, db: Session = Depends(get_db)):
    """Remove uma resposta predefinida"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    respostas = config.get("respostas", [])
    config["respostas"] = [r for r in respostas if r.get("id") != resposta_id]
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Resposta removida"}


# ========== MENU INTERATIVO ==========
@router.get("/{order_id}/menu", response_model=List[OpcaoMenu])
def get_menu(order_id: int, db: Session = Depends(get_db)):
    """Retorna todas as opções do menu"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}
    return config.get("menu", [])


@router.post("/{order_id}/menu")
def add_menu_option(order_id: int, opcao: OpcaoMenu, db: Session = Depends(get_db)):
    """Adiciona uma opção ao menu"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    if "menu" not in config:
        config["menu"] = []

    novo_id = max([m.get("id", 0) for m in config["menu"]], default=0) + 1
    opcao_dict = opcao.dict()
    opcao_dict["id"] = novo_id

    config["menu"].append(opcao_dict)
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Opção adicionada", "id": novo_id}


@router.put("/{order_id}/menu/{menu_id}")
def update_menu_option(order_id: int, menu_id: int, opcao: OpcaoMenu, db: Session = Depends(get_db)):
    """Atualiza uma opção do menu"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    menu = config.get("menu", [])
    for i, m in enumerate(menu):
        if m.get("id") == menu_id:
            opcao_dict = opcao.dict()
            opcao_dict["id"] = menu_id
            menu[i] = opcao_dict
            config["menu"] = menu
            order.configuracao_agente = json.dumps(config, ensure_ascii=False)
            db.commit()
            return {"message": "Opção atualizada"}

    raise HTTPException(status_code=404, detail="Opção não encontrada")


@router.delete("/{order_id}/menu/{menu_id}")
def delete_menu_option(order_id: int, menu_id: int, db: Session = Depends(get_db)):
    """Remove uma opção do menu"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    menu = config.get("menu", [])
    config["menu"] = [m for m in menu if m.get("id") != menu_id]
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Opção removida"}


# ========== FLUXOS DE CONVERSA ==========
@router.get("/{order_id}/fluxos", response_model=List[FluxoConversa])
def get_fluxos(order_id: int, db: Session = Depends(get_db)):
    """Retorna todos os fluxos de conversa"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}
    return config.get("fluxos", [])


@router.post("/{order_id}/fluxos")
def add_fluxo(order_id: int, fluxo: FluxoConversa, db: Session = Depends(get_db)):
    """Adiciona um novo fluxo de conversa"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    if "fluxos" not in config:
        config["fluxos"] = []

    novo_id = max([f.get("id", 0) for f in config["fluxos"]], default=0) + 1
    fluxo_dict = fluxo.dict()
    fluxo_dict["id"] = novo_id

    config["fluxos"].append(fluxo_dict)
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Fluxo adicionado", "id": novo_id}


@router.put("/{order_id}/fluxos/{fluxo_id}")
def update_fluxo(order_id: int, fluxo_id: int, fluxo: FluxoConversa, db: Session = Depends(get_db)):
    """Atualiza um fluxo de conversa"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    fluxos = config.get("fluxos", [])
    for i, f in enumerate(fluxos):
        if f.get("id") == fluxo_id:
            fluxo_dict = fluxo.dict()
            fluxo_dict["id"] = fluxo_id
            fluxos[i] = fluxo_dict
            config["fluxos"] = fluxos
            order.configuracao_agente = json.dumps(config, ensure_ascii=False)
            db.commit()
            return {"message": "Fluxo atualizado"}

    raise HTTPException(status_code=404, detail="Fluxo não encontrado")


@router.delete("/{order_id}/fluxos/{fluxo_id}")
def delete_fluxo(order_id: int, fluxo_id: int, db: Session = Depends(get_db)):
    """Remove um fluxo de conversa"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    fluxos = config.get("fluxos", [])
    config["fluxos"] = [f for f in fluxos if f.get("id") != fluxo_id]
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Fluxo removido"}


# ========== INTEGRAÇÕES ==========
@router.get("/{order_id}/integracoes", response_model=List[Integracao])
def get_integracoes(order_id: int, db: Session = Depends(get_db)):
    """Retorna todas as integrações"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}
    return config.get("integracoes", [])


@router.post("/{order_id}/integracoes")
def add_integracao(order_id: int, integracao: Integracao, db: Session = Depends(get_db)):
    """Adiciona uma nova integração"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    if "integracoes" not in config:
        config["integracoes"] = []

    novo_id = max([i.get("id", 0) for i in config["integracoes"]], default=0) + 1
    integracao_dict = integracao.dict()
    integracao_dict["id"] = novo_id

    config["integracoes"].append(integracao_dict)
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Integração adicionada", "id": novo_id}


@router.put("/{order_id}/integracoes/{integracao_id}")
def update_integracao(order_id: int, integracao_id: int, integracao: Integracao, db: Session = Depends(get_db)):
    """Atualiza uma integração"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    integracoes = config.get("integracoes", [])
    for i, integ in enumerate(integracoes):
        if integ.get("id") == integracao_id:
            integracao_dict = integracao.dict()
            integracao_dict["id"] = integracao_id
            integracoes[i] = integracao_dict
            config["integracoes"] = integracoes
            order.configuracao_agente = json.dumps(config, ensure_ascii=False)
            db.commit()
            return {"message": "Integração atualizada"}

    raise HTTPException(status_code=404, detail="Integração não encontrada")


@router.delete("/{order_id}/integracoes/{integracao_id}")
def delete_integracao(order_id: int, integracao_id: int, db: Session = Depends(get_db)):
    """Remove uma integração"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config = json.loads(order.configuracao_agente) if order.configuracao_agente else {}

    integracoes = config.get("integracoes", [])
    config["integracoes"] = [i for i in integracoes if i.get("id") != integracao_id]
    order.configuracao_agente = json.dumps(config, ensure_ascii=False)

    db.commit()
    return {"message": "Integração removida"}


# ========== ATENDENTES ==========
class AtendenteAdd(BaseModel):
    numero: str


@router.get("/{order_id}/atendentes")
def get_atendentes(order_id: int, db: Session = Depends(get_db)):
    """Retorna lista de números de atendentes"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar ou criar ConfiguracaoBot
    config_bot = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == order_id
    ).first()

    if not config_bot or not config_bot.numeros_atendentes:
        return []

    try:
        atendentes = json.loads(config_bot.numeros_atendentes)
        return [{"numero": num} for num in atendentes]
    except json.JSONDecodeError:
        return []


@router.post("/{order_id}/atendentes")
def add_atendente(order_id: int, data: AtendenteAdd, db: Session = Depends(get_db)):
    """Adiciona um número de atendente"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar ou criar ConfiguracaoBot
    config_bot = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == order_id
    ).first()

    if not config_bot:
        config_bot = models.ConfiguracaoBot(pedido_id=order_id, numeros_atendentes="[]")
        db.add(config_bot)
        db.flush()

    # Parse números existentes
    try:
        atendentes = json.loads(config_bot.numeros_atendentes) if config_bot.numeros_atendentes else []
    except json.JSONDecodeError:
        atendentes = []

    # Verificar se já existe
    if data.numero in atendentes:
        raise HTTPException(status_code=400, detail="Atendente já cadastrado")

    # Adicionar novo número
    atendentes.append(data.numero)
    config_bot.numeros_atendentes = json.dumps(atendentes)

    db.commit()
    return {"message": "Atendente adicionado", "numero": data.numero}


@router.delete("/{order_id}/atendentes/{numero}")
def remove_atendente(order_id: int, numero: str, db: Session = Depends(get_db)):
    """Remove um número de atendente"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    config_bot = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == order_id
    ).first()

    if not config_bot or not config_bot.numeros_atendentes:
        raise HTTPException(status_code=404, detail="Nenhum atendente cadastrado")

    try:
        atendentes = json.loads(config_bot.numeros_atendentes)
    except json.JSONDecodeError:
        atendentes = []

    if numero not in atendentes:
        raise HTTPException(status_code=404, detail="Atendente não encontrado")

    atendentes.remove(numero)
    config_bot.numeros_atendentes = json.dumps(atendentes)

    db.commit()
    return {"message": "Atendente removido"}
