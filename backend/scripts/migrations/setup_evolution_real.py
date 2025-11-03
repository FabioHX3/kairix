#!/usr/bin/env python3
"""
Script para configurar Evolution API com os dados REAIS do .env
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from database import SessionLocal
from models import ConfiguracaoBot, Pedido
import httpx

# Carregar .env da RAIZ do projeto
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

def setup_evolution():
    """Configura Evolution API"""

    # Pegar variáveis do .env REAL
    evolution_url = os.getenv('EVOLUTION_URL', '')
    evolution_key = os.getenv('EVOLUTION_API_KEY', '')

    print("=" * 70)
    print("🚀 CONFIGURANDO EVOLUTION API")
    print("=" * 70)
    print(f"\n📍 URL: {evolution_url}")
    print(f"🔑 API Key: {'***' + evolution_key[-10:] if len(evolution_key) > 10 else 'VAZIA'}")

    if not evolution_url or not evolution_key:
        print("\n❌ ERRO: Variáveis EVOLUTION_URL ou EVOLUTION_API_KEY não encontradas!")
        return False

    # Conectar ao banco
    db = SessionLocal()

    try:
        # Buscar pedido
        pedido = db.query(Pedido).filter(Pedido.id == 1).first()
        if not pedido:
            print("\n❌ Pedido ID 1 não encontrado")
            return False

        print(f"\n✅ Pedido encontrado: #{pedido.id}")

        # Testar conexão PRIMEIRO
        print(f"\n🔌 Testando conexão com Evolution...")
        try:
            response = httpx.get(
                f"{evolution_url.rstrip('/manager')}/instance/fetchInstances",
                headers={"apikey": evolution_key},
                timeout=10.0
            )

            if response.status_code == 200:
                instances = response.json()
                print(f"✅ Conexão OK! {len(instances)} instância(s) encontrada(s)")

                # Mostrar instâncias
                for inst in instances:
                    nome = inst.get('name', 'N/A')
                    status = inst.get('connectionStatus', 'N/A')
                    numero = inst.get('number', 'N/A')
                    print(f"\n   📱 Instância: {nome}")
                    print(f"   📊 Status: {status}")
                    print(f"   📞 Número: {numero}")

                # Pegar nome da primeira instância
                instance_name = instances[0].get('name', 'Chrystian') if instances else 'Chrystian'

            else:
                print(f"⚠️  Evolution respondeu com status {response.status_code}")
                print(f"   {response.text[:300]}")
                instance_name = 'Chrystian'

        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            print("   Continuando com instância 'Chrystian'...")
            instance_name = 'Chrystian'

        # Salvar no banco
        print(f"\n💾 Salvando configuração no banco...")

        config = db.query(ConfiguracaoBot).filter(
            ConfiguracaoBot.pedido_id == 1
        ).first()

        if not config:
            config = ConfiguracaoBot(
                pedido_id=1,
                mensagem_boas_vindas="Olá! 👋 Bem-vindo ao atendimento automático da Kairix. Como posso ajudar você hoje?",
                mensagem_nao_entendida="Desculpe, não entendi sua mensagem. 🤔\n\nDigite *menu* para ver as opções disponíveis."
            )
            db.add(config)
            print("   📝 Nova configuração criada")
        else:
            print("   📝 Atualizando configuração existente")

        # URL sem o /manager
        base_url = evolution_url.rstrip('/manager')

        config.evolution_url = base_url
        config.evolution_key = evolution_key
        config.evolution_instance = instance_name
        config.ativo = True

        db.commit()
        db.refresh(config)

        print("   ✅ Salvo com sucesso!")
        print(f"\n   📍 URL: {base_url}")
        print(f"   🏷️  Instância: {instance_name}")

        # Gerar URL do webhook
        webhook_url = f"http://localhost:8012/api/evolution/webhook/1"

        print("\n" + "=" * 70)
        print("✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("=" * 70)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("\n1️⃣  Configure o Webhook no Evolution:")
        print(f"   • Acesse: {evolution_url}")
        print(f"   • Vá em Instância '{instance_name}' → Webhooks")
        print(f"   • URL do Webhook: {webhook_url}")
        print("   • Eventos: messages.upsert")
        print("   • Salve")

        print("\n2️⃣  Configure o Menu no Painel:")
        print("   • Acesse: http://localhost:8012/configurar?orderId=1")
        print("   • Crie opções de menu")
        print("   • Adicione respostas rápidas")

        print("\n3️⃣  Teste enviando uma mensagem WhatsApp!")
        print("=" * 70)

        return True

    finally:
        db.close()

if __name__ == "__main__":
    success = setup_evolution()
    sys.exit(0 if success else 1)
