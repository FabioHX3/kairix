#!/usr/bin/env python3
"""
Script para configurar Evolution API usando variáveis do .env
"""
import os
from dotenv import load_dotenv
from database import SessionLocal
from models import ConfiguracaoBot, Pedido
import httpx

# Carregar .env
load_dotenv()

def setup_evolution():
    """Configura Evolution API a partir do .env"""

    # Pegar variáveis do .env
    evolution_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
    evolution_key = os.getenv('EVOLUTION_API_KEY', '')
    evolution_instance = os.getenv('EVOLUTION_INSTANCE_NAME', 'kairix')

    print("🔧 Configurando Evolution API...")
    print(f"   URL: {evolution_url}")
    print(f"   Instance: {evolution_instance}")
    print(f"   API Key: {'***' + evolution_key[-4:] if len(evolution_key) > 4 else 'NÃO CONFIGURADA'}")

    if not evolution_key or evolution_key == 'sua_api_key_aqui':
        print("\n⚠️  ATENÇÃO: API Key não está configurada no .env!")
        print("   Edite o arquivo .env e adicione a sua EVOLUTION_API_KEY real")
        return False

    # Conectar ao banco
    db = SessionLocal()

    try:
        # Verificar se existe pedido
        pedido = db.query(Pedido).filter(Pedido.id == 1).first()
        if not pedido:
            print("❌ Pedido ID 1 não encontrado no banco")
            return False

        print(f"\n✅ Pedido encontrado: ID {pedido.id}")

        # Buscar ou criar configuração
        config = db.query(ConfiguracaoBot).filter(
            ConfiguracaoBot.pedido_id == 1
        ).first()

        if not config:
            print("📝 Criando nova configuração...")
            config = ConfiguracaoBot(
                pedido_id=1,
                mensagem_boas_vindas="Olá! Bem-vindo ao atendimento automático. Como posso ajudar?",
                mensagem_nao_entendida="Desculpe, não entendi. Digite *menu* para ver as opções."
            )
            db.add(config)
        else:
            print("📝 Atualizando configuração existente...")

        # Atualizar dados Evolution
        config.evolution_url = evolution_url
        config.evolution_key = evolution_key
        config.evolution_instance = evolution_instance
        config.ativo = True

        db.commit()
        db.refresh(config)

        print("✅ Configuração salva no banco de dados!")

        # Testar conexão
        print("\n🔌 Testando conexão com Evolution API...")
        try:
            response = httpx.get(
                f"{evolution_url}/instance/fetchInstances",
                headers={"apikey": evolution_key},
                timeout=5.0
            )

            if response.status_code == 200:
                print("✅ Conexão com Evolution estabelecida!")
                data = response.json()
                print(f"   Instâncias encontradas: {len(data) if isinstance(data, list) else 'N/A'}")
                return True
            else:
                print(f"⚠️  Evolution respondeu com status {response.status_code}")
                print(f"   Resposta: {response.text[:200]}")
                return False

        except httpx.ConnectError:
            print(f"❌ Não conseguiu conectar em {evolution_url}")
            print("   Verifique se:")
            print("   1. O Evolution API está rodando")
            print("   2. A URL está correta no .env")
            print("   3. Não há firewall bloqueando")
            return False
        except Exception as e:
            print(f"❌ Erro ao testar conexão: {e}")
            return False

    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 CONFIGURAÇÃO EVOLUTION API DO .ENV")
    print("=" * 60)

    success = setup_evolution()

    print("\n" + "=" * 60)
    if success:
        print("✅ TUDO PRONTO!")
        print("\nPRÓXIMOS PASSOS:")
        print("1. Configure o webhook no Evolution:")
        print("   URL: http://SEU_DOMINIO/api/evolution/webhook/1")
        print("   Eventos: messages.upsert")
        print("\n2. Acesse o painel de configuração:")
        print("   http://localhost:8012/configurar?orderId=1")
        print("\n3. Configure menu, respostas rápidas, etc")
    else:
        print("❌ FALHOU - Verifique os problemas acima")
    print("=" * 60)
