"""
Helper para criação e gerenciamento automático de instâncias Evolution API
"""
import os
import requests
import re
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import models
import config_helper


def limpar_numero_whatsapp(numero: str) -> str:
    """
    Remove caracteres especiais do número de WhatsApp.
    Retorna apenas dígitos.
    """
    return re.sub(r'[^0-9]', '', numero)


def gerar_nome_instancia(cliente_id: int, numero: str) -> str:
    """
    Gera nome único para a instância baseado no ID do cliente e número.
    Ex: kairix_cliente_1_5565999342609
    """
    numero_limpo = limpar_numero_whatsapp(numero)
    return f"kairix_cliente_{cliente_id}_{numero_limpo}"


async def criar_instancia_evolution(
    db: Session,
    cliente: models.Cliente,
    pedido: models.Pedido
) -> Dict[str, Any]:
    """
    Cria uma nova instância no Evolution API para o cliente.

    Args:
        db: Sessão do banco de dados
        cliente: Objeto do cliente
        pedido: Objeto do pedido

    Returns:
        Dict com informações da instância criada
    """

    # Buscar configurações do Evolution do banco
    evolution_url = config_helper.get_evolution_api_url(db)
    evolution_key = config_helper.get_evolution_api_key(db)
    kairix_url = os.getenv("KAIRIX_PUBLIC_URL", "http://localhost:8012")

    # Gerar nome único da instância
    numero_limpo = limpar_numero_whatsapp(cliente.whatsapp)
    instance_name = gerar_nome_instancia(cliente.id, cliente.whatsapp)

    # Configurações da instância
    instance_data = {
        "instanceName": instance_name,
        "token": evolution_key,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",
        "number": numero_limpo,
        "webhookUrl": f"{kairix_url}/api/evolution/webhook",
        "webhookByEvents": True,
        "webhookBase64": False,
        "webhookEvents": [
            "QRCODE_UPDATED",
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "MESSAGES_DELETE",
            "SEND_MESSAGE",
            "CONNECTION_UPDATE",
            "CALL",
            "NEW_JWT_TOKEN"
        ]
    }

    try:
        # Criar instância
        headers = {
            "apikey": evolution_key,
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{evolution_url}/instance/create",
            json=instance_data,
            headers=headers,
            timeout=30
        )

        if response.status_code in [200, 201]:
            result = response.json()

            # Atualizar configuração do bot com dados da instância
            config = db.query(models.ConfiguracaoBot).filter(
                models.ConfiguracaoBot.pedido_id == pedido.id
            ).first()

            if config:
                config.evolution_url = evolution_url
                config.evolution_key = evolution_key
                config.evolution_instance = instance_name
                db.commit()

            return {
                "success": True,
                "instance_name": instance_name,
                "numero": numero_limpo,
                "qrcode": result.get("qrcode"),
                "data": result
            }
        else:
            error_msg = response.text
            print(f"Erro ao criar instância Evolution: {error_msg}")
            return {
                "success": False,
                "error": f"Erro ao criar instância: {response.status_code}",
                "details": error_msg
            }

    except Exception as e:
        print(f"Exceção ao criar instância Evolution: {str(e)}")
        return {
            "success": False,
            "error": f"Exceção: {str(e)}"
        }


def obter_qrcode_instancia(evolution_url: str, evolution_key: str, instance_name: str) -> Optional[Dict]:
    """
    Obtém o QR Code de uma instância.
    """
    try:
        headers = {"apikey": evolution_key}
        response = requests.get(
            f"{evolution_url}/instance/connect/{instance_name}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Erro ao obter QR Code: {str(e)}")
        return None


def verificar_status_instancia(evolution_url: str, evolution_key: str, instance_name: str) -> Optional[Dict]:
    """
    Verifica o status de conexão de uma instância.
    """
    try:
        headers = {"apikey": evolution_key}
        response = requests.get(
            f"{evolution_url}/instance/connectionState/{instance_name}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Erro ao verificar status: {str(e)}")
        return None


def deletar_instancia(evolution_url: str, evolution_key: str, instance_name: str) -> bool:
    """
    Deleta uma instância do Evolution API.
    """
    try:
        headers = {"apikey": evolution_key}
        response = requests.delete(
            f"{evolution_url}/instance/delete/{instance_name}",
            headers=headers,
            timeout=30
        )

        return response.status_code in [200, 204]
    except Exception as e:
        print(f"Erro ao deletar instância: {str(e)}")
        return False
