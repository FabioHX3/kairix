#!/usr/bin/env python3
"""
Script para verificar configuração do webhook no Evolution
"""
import requests
import json
from dotenv import load_dotenv
import os

# Carregar .env da raiz
load_dotenv('/mnt/c/PROJETOS/kairix/.env')

EVOLUTION_URL = os.getenv('EVOLUTION_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')

def verificar_webhook():
    """Verifica o webhook configurado na instância"""

    print(f"🔍 Verificando webhook na instância 'Chrystian'...")
    print(f"📡 Evolution URL: {EVOLUTION_URL}")

    # Buscar instância
    url = f"{EVOLUTION_URL}/instance/fetchInstances"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        instances = response.json()
        print(f"\n✅ Encontradas {len(instances)} instâncias")

        # Procurar instância Chrystian
        chrystian = None
        for instance in instances:
            if instance.get('instance', {}).get('instanceName') == 'Chrystian':
                chrystian = instance
                break

        if not chrystian:
            print("❌ Instância 'Chrystian' não encontrada!")
            return

        print(f"\n📱 Instância: Chrystian")
        print(f"   Status: {chrystian.get('instance', {}).get('status', 'N/A')}")

        # Verificar webhook configurado
        webhook = chrystian.get('instance', {}).get('webhook')

        if webhook:
            print(f"\n🔗 Webhook configurado:")
            print(f"   URL: {webhook.get('url', 'N/A')}")
            print(f"   Enabled: {webhook.get('enabled', False)}")
            print(f"   Events: {webhook.get('events', [])}")
        else:
            print("\n❌ Nenhum webhook configurado!")
            print("\n📝 Para configurar, use:")
            print(f"   POST {EVOLUTION_URL}/webhook/set/Chrystian")
            print(f"   Body:")
            print(f"""   {{
      "url": "https://thick-pigs-listen.loca.lt/api/evolution/webhook/1",
      "enabled": true,
      "events": ["messages.upsert"]
   }}""")

        return chrystian

    except Exception as e:
        print(f"❌ Erro ao verificar: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return None

def configurar_webhook():
    """Configura o webhook na instância"""

    print("\n🔧 Configurando webhook...")

    url = f"{EVOLUTION_URL}/webhook/set/Chrystian"
    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "url": "https://thick-pigs-listen.loca.lt/api/evolution/webhook/1",
        "enabled": True,
        "events": ["messages.upsert"],
        "webhook_by_events": False
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Webhook configurado com sucesso!")
        print(f"   Response: {json.dumps(result, indent=2)}")
        return True

    except Exception as e:
        print(f"❌ Erro ao configurar: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return False

if __name__ == "__main__":
    print("="*70)
    print("🔍 VERIFICAÇÃO DE WEBHOOK DO EVOLUTION")
    print("="*70)

    instance = verificar_webhook()

    if instance:
        webhook = instance.get('instance', {}).get('webhook')
        if not webhook or not webhook.get('enabled'):
            print("\n❓ Deseja configurar o webhook agora? (s/n)")
            resposta = input().lower()
            if resposta == 's':
                configurar_webhook()
                print("\n✅ Configuração concluída! Teste enviando uma mensagem.")

    print("="*70)
