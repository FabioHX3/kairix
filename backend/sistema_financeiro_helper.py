"""
Helper para integração com o Kairix Financeiro
"""
import requests
from sqlalchemy.orm import Session
from typing import Dict, Optional
import crud
import models


async def cadastrar_usuario_sistema_financeiro(
    db: Session,
    cliente: models.Cliente,
    pedido: models.Pedido
) -> Dict:
    """
    Cria um usuário no sistema financeiro após o pagamento ser aprovado.

    Args:
        db: Sessão do banco de dados
        cliente: Cliente que foi ativado
        pedido: Pedido que foi pago

    Returns:
        Dict com informações sobre o resultado:
        {
            "success": bool,
            "user_id": int (se sucesso),
            "message": str,
            "error": str (se falha)
        }
    """
    try:
        # Buscar configurações do sistema
        config = crud.get_configuracao_sistema(db)

        if not config.sistema_financeiro_url:
            return {
                "success": False,
                "error": "Sistema Financeiro não configurado"
            }

        # Preparar dados do usuário para cadastro
        usuario_data = {
            "nome": cliente.nome,
            "email": cliente.email,
            "senha": cliente.whatsapp,  # Usar whatsapp como senha inicial
            "telefone": cliente.telefone,
            "empresa": cliente.nome_empresa or cliente.nome,
            "cpf_cnpj": cliente.cpf_cnpj,
            "ativo": True,
            # Informações adicionais
            "plano": pedido.plano.nome if pedido.plano else "N/A",
            "origem": "kairix_auto"
        }

        # Headers para a requisição
        headers = {
            "Content-Type": "application/json"
        }

        if config.sistema_financeiro_api_key:
            headers["Authorization"] = f"Bearer {config.sistema_financeiro_api_key}"

        # Fazer requisição para criar usuário
        url = f"{config.sistema_financeiro_url.rstrip('/')}/api/auth/cadastro"

        response = requests.post(
            url,
            json=usuario_data,
            headers=headers,
            timeout=15
        )

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "user_id": result.get("id") or result.get("user_id"),
                "message": "Usuário criado com sucesso no sistema financeiro",
                "data": result
            }
        elif response.status_code == 409:
            # Usuário já existe
            return {
                "success": False,
                "error": "Usuário já existe no sistema financeiro",
                "status_code": 409
            }
        else:
            return {
                "success": False,
                "error": f"Erro ao criar usuário: HTTP {response.status_code}",
                "details": response.text[:500] if response.text else "Sem detalhes",
                "status_code": response.status_code
            }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout ao conectar com Sistema Financeiro"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Erro de conexão com Sistema Financeiro"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro inesperado: {str(e)}"
        }


async def gerar_token_autenticacao_sistema_financeiro(
    db: Session,
    cliente: models.Cliente
) -> Optional[Dict]:
    """
    Gera um token de autenticação no sistema financeiro para redirecionar o usuário já logado.

    Args:
        db: Sessão do banco de dados
        cliente: Cliente que está fazendo login

    Returns:
        Dict com token e URL de redirecionamento ou None se falhar:
        {
            "success": bool,
            "token": str,
            "redirect_url": str,
            "error": str (se falha)
        }
    """
    try:
        # Buscar configurações do sistema
        config = crud.get_configuracao_sistema(db)

        if not config.sistema_financeiro_url:
            return {
                "success": False,
                "error": "Sistema Financeiro não configurado"
            }

        # Preparar credenciais para login
        login_data = {
            "email": cliente.email,
            "senha": cliente.whatsapp  # Senha inicial é o whatsapp
        }

        # Headers para a requisição
        headers = {
            "Content-Type": "application/json"
        }

        if config.sistema_financeiro_api_key:
            headers["Authorization"] = f"Bearer {config.sistema_financeiro_api_key}"

        # Fazer requisição de login para obter token
        url = f"{config.sistema_financeiro_url.rstrip('/')}/api/auth/login"

        response = requests.post(
            url,
            json=login_data,
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            token = result.get("token") or result.get("access_token")

            if token:
                # Construir URL de redirecionamento com token
                redirect_url = f"{config.sistema_financeiro_url.rstrip('/')}/dashboard?token={token}"

                return {
                    "success": True,
                    "token": token,
                    "redirect_url": redirect_url
                }
            else:
                return {
                    "success": False,
                    "error": "Token não retornado pela API"
                }
        else:
            return {
                "success": False,
                "error": f"Erro ao autenticar: HTTP {response.status_code}",
                "status_code": response.status_code
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao gerar token: {str(e)}"
        }
