from fastapi import FastAPI, Request, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Importar routers
from routers import plans, clients, orders, auth, config, admin, evolution, conversas, knowledge

# Importar database e models
import database
import models
import crud

# Carregar variáveis de ambiente
load_dotenv()

# Criar tabelas no banco
models.Base.metadata.create_all(bind=database.engine)

# Criar aplicação FastAPI
app = FastAPI(
    title="Kairix API",
    description="API para gestão de vendas e soluções Kairix",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(plans.router)
app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(config.router)
app.include_router(admin.router)
app.include_router(evolution.router)
app.include_router(conversas.router)
app.include_router(knowledge.router)

# Servir arquivos estáticos do backend
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar Jinja2 Templates
templates = Jinja2Templates(directory="templates")

# Diretório raiz do projeto (onde estão os HTMLs do site)
BASE_DIR = Path(__file__).resolve().parent.parent


# ========== FUNÇÃO AUXILIAR PARA BUSCAR DADOS DO CLIENTE ==========
def get_client_panel_data(client_id: Optional[str]):
    """
    Busca dados do cliente e pedido para exibir no painel.
    Retorna um dicionário com os dados ou None se não encontrar.
    """
    if not client_id:
        return None

    try:
        client_id_int = int(client_id)
    except:
        return None

    # Criar sessão do banco
    db = next(database.get_db())

    try:
        # Buscar cliente
        client = crud.get_client(db, client_id_int)
        if not client:
            return None

        # Buscar pedidos do cliente
        orders = crud.get_orders_by_client(db, client_id_int)

        # Dados padrão
        data = {
            "client_id": client.id,
            "client_name": client.nome,
            "client_email": client.email,
            "product_name": "Kairix Bot",
            "plan_name": "Sem Plano",
            "plan_type": None,
            "show_base_conhecimento": False
        }

        # Se tem pedido, buscar dados do plano
        if orders and len(orders) > 0:
            order = orders[0]  # Pedido mais recente
            plan = crud.get_plan(db, order.plano_id)

            if plan:
                data["product_name"] = plan.nome
                data["plan_name"] = plan.nome
                data["plan_type"] = plan.tipo

                # Mostrar base de conhecimento apenas para Agente IA
                data["show_base_conhecimento"] = (plan.tipo == models.TipoPlano.AGENTE_IA)

        return data

    finally:
        db.close()


@app.get("/")
def read_root():
    """Página inicial do site"""
    return FileResponse(BASE_DIR / "index.html")


@app.get("/cadastro")
def cadastro_page():
    """Página de cadastro de clientes"""
    return FileResponse("static/cadastro.html")


@app.get("/login")
def login_page():
    """Página de login do cliente"""
    return FileResponse("static/login.html")




@app.get("/painel")
def painel_page():
    """Painel de configuração - redireciona para dashboard"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/painel/dashboard", status_code=301)


# ========== NOVAS ROTAS COM JINJA2 TEMPLATES ==========

@app.get("/painel/dashboard")
async def dashboard_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Dashboard - Nova interface modular com Jinja2"""
    # Buscar dados reais do cliente
    client_data = get_client_panel_data(client_id)

    if not client_data:
        # Se não tiver cookie ou cliente não encontrado, usa dados padrão
        client_data = {
            "product_name": "Kairix Bot",
            "plan_name": "Plano Teste",
            "show_base_conhecimento": False
        }

    # Buscar dados reais de configuração
    db = next(database.get_db())
    config_data = {
        "evolution_instance": None,
        "respostas_count": 0,
        "menu_interativo": None,
        "documentos_count": 0,
        "modelo_ia_configurado": False,
        "rag_configurado": False
    }

    try:
        # Buscar pedido do cliente
        client_id_int = int(client_id) if client_id else None
        if client_id_int:
            orders = crud.get_orders_by_client(db, client_id_int)
            if orders and len(orders) > 0:
                pedido_id = orders[0].id

                # Buscar ConfiguracaoBot
                config_bot = db.query(models.ConfiguracaoBot).filter(
                    models.ConfiguracaoBot.pedido_id == pedido_id
                ).first()

                if config_bot:
                    config_data["evolution_instance"] = config_bot.evolution_instance
                    config_data["menu_interativo"] = config_bot.menu_interativo

                    # Contar respostas rápidas
                    if config_bot.respostas_rapidas:
                        try:
                            import json
                            respostas = json.loads(config_bot.respostas_rapidas)
                            config_data["respostas_count"] = len(respostas) if isinstance(respostas, list) else 0
                        except:
                            config_data["respostas_count"] = 0

                    # Contar documentos na base de conhecimento
                    if config_bot.evolution_instance:
                        knowledge_path = Path("storage/knowledge_base") / config_bot.evolution_instance
                        if knowledge_path.exists():
                            config_data["documentos_count"] = len([f for f in knowledge_path.iterdir() if f.is_file()])

        # Buscar configuração do sistema (IA e RAG) - é global
        config_sistema = db.query(models.ConfiguracaoSistema).first()
        if config_sistema:
            config_data["modelo_ia_configurado"] = bool(config_sistema.ollama_url and config_sistema.ollama_model)
            config_data["rag_configurado"] = bool(config_sistema.qdrant_url and config_sistema.rag_chunk_size)

    except Exception as e:
        print(f"❌ Erro ao buscar configurações: {e}")
    finally:
        db.close()

    return templates.TemplateResponse("painel/dashboard.html", {
        "request": request,
        "active_page": "dashboard",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "plan_type": client_data.get("plan_type"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False),
        "stats": {
            "total_mensagens": 0,
            "total_contatos": 0
        },
        "config": config_data,
        "conversas_recentes": []
    })


@app.get("/painel/conversas")
async def conversas_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Conversas - Visualização de conversas e mensagens"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/conversas.html", {
        "request": request,
        "active_page": "conversas",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False),
        "stats": {
            "total_conversas": 0,
            "conversas_ativas": 0,
            "total_mensagens": 0,
            "tempo_medio": "0s"
        }
    })


@app.get("/painel/conexao")
async def conexao_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Conexão WhatsApp - Configuração do número"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/conexao.html", {
        "request": request,
        "active_page": "conexao",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "config": {
            "numero_whatsapp": ""
        }
    })


@app.get("/painel/respostas")
async def respostas_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Respostas Predefinidas - Configuração de respostas automáticas"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/respostas.html", {
        "request": request,
        "active_page": "respostas",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False)
    })


@app.get("/painel/base-conhecimento")
async def base_conhecimento_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Base de Conhecimento - Gerenciamento de documentos RAG"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/base-conhecimento.html", {
        "request": request,
        "active_page": "base-conhecimento",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False)
    })


@app.get("/painel/atendentes")
async def atendentes_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Atendentes - Gerenciamento de atendentes humanos"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/atendentes.html", {
        "request": request,
        "active_page": "atendentes",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False)
    })


@app.get("/painel/menu")
async def menu_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Menu Interativo - Configuração de menus"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/menu.html", {
        "request": request,
        "active_page": "menu",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False)
    })


@app.get("/painel/fluxos")
async def fluxos_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Fluxos de Conversa - Criação de fluxos automáticos"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/fluxos.html", {
        "request": request,
        "active_page": "fluxos",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False)
    })


@app.get("/painel/integracoes")
async def integracoes_page(request: Request, client_id: Optional[str] = Cookie(None)):
    """Integrações - Configuração de integrações externas"""
    client_data = get_client_panel_data(client_id) or {}
    return templates.TemplateResponse("painel/integracoes.html", {
        "request": request,
        "active_page": "integracoes",
        "product_name": client_data.get("product_name", "Kairix Bot"),
        "plan_name": client_data.get("plan_name", "Sem Plano"),
        "show_base_conhecimento": client_data.get("show_base_conhecimento", False),
        "webhook_url": "https://seu-dominio.com/webhook/evolution/pedido-1"
    })


# Redirect antigo para novo (compatibilidade)
@app.get("/configurar")
def configurar_redirect():
    """Redirect de /configurar para /painel"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/painel", status_code=301)


@app.get("/configurar-v2")
def configurar_v2_page():
    """Página de configuração do bot (Nova Interface Simplificada)"""
    return FileResponse("static/configurar-v2.html")


@app.get("/financeiro")
def financeiro_page():
    """Página de gestão financeira"""
    return FileResponse("static/financeiro.html")


@app.get("/teste-config")
def teste_config_page():
    """Página de teste de configuração"""
    return FileResponse("static/teste-config.html")


@app.get("/set-cookie-test")
def set_cookie_test_page():
    """Página para configurar cookie de teste"""
    return FileResponse("static/set-cookie-test.html")


@app.get("/admin/login")
def admin_login_page():
    """Página de Login do Admin"""
    return FileResponse("static/admin-login.html")


@app.get("/admin")
def admin_page():
    """Painel Administrativo"""
    return FileResponse("static/admin.html")


@app.get("/cliente/login")
def cliente_login_page():
    """Página de Login do Cliente"""
    return FileResponse("static/cliente-login.html")


@app.get("/cliente")
def cliente_page():
    """Painel do Cliente"""
    return FileResponse("static/cliente.html")


@app.get("/conectar-evolution")
def conectar_evolution_page():
    """Página para conectar Evolution API"""
    return FileResponse("static/conectar-evolution.html")


@app.get("/teste-webhook")
def teste_webhook_page():
    """Página de teste de webhook"""
    return FileResponse("static/teste_webhook.html")


@app.get("/base-conhecimento")
def base_conhecimento_page():
    """Página de gerenciamento da Base de Conhecimento do Agente IA"""
    return FileResponse("static/base-conhecimento.html")


# Rotas para páginas do site
@app.get("/bot-ia.html")
def bot_ia_page():
    """Página do Bot com IA"""
    return FileResponse(BASE_DIR / "bot-ia.html")


@app.get("/bot-normal.html")
def bot_normal_page():
    """Página do Bot Normal"""
    return FileResponse(BASE_DIR / "bot-normal.html")


@app.get("/agente-financeiro.html")
def agente_financeiro_page():
    """Página do Agente Financeiro"""
    return FileResponse(BASE_DIR / "agente-financeiro.html")


# Servir arquivos estáticos do site (logo, vídeos, etc.)
@app.get("/logo.png")
def logo_file():
    """Logo do site"""
    return FileResponse(BASE_DIR / "logo.png")


@app.get("/fundo.mp4")
def video_file():
    """Vídeo de fundo"""
    return FileResponse(BASE_DIR / "fundo.mp4")


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8012))
    reload = os.getenv("RELOAD", "False").lower() == "true"

    uvicorn.run("main:app", host=host, port=port, reload=reload)
