#!/usr/bin/env python3
"""
Script para criar menu de exemplo com submenus
"""
from database import SessionLocal
from models import Pedido
import json

def criar_menu_exemplo():
    """Cria menu completo de exemplo"""

    db = SessionLocal()

    try:
        # Buscar pedido
        pedido = db.query(Pedido).filter(Pedido.id == 1).first()
        if not pedido:
            print("❌ Pedido não encontrado")
            return False

        print("📋 Criando menu de exemplo...")

        # Menu completo com submenus
        menu = [
            {
                "id": 1,
                "numero": "1",
                "titulo": "🛍️ Nossos Produtos",
                "descricao": "Veja nossos planos e produtos",
                "acao": "submenu",
                "submenu": json.dumps([
                    {
                        "numero": "1",
                        "titulo": "Bot Normal",
                        "resposta": "🤖 *Bot Normal*\n\nAtendimento automatizado inteligente:\n\n💰 A partir de R$ 99/mês\n✅ Respostas rápidas\n✅ Menu interativo\n✅ Integração WhatsApp\n\nInteresse? Digite *quero contratar*"
                    },
                    {
                        "numero": "2",
                        "titulo": "Bot com IA",
                        "resposta": "🧠 *Bot com IA*\n\nInteligência Artificial avançada:\n\n💰 A partir de R$ 299/mês\n✅ Tudo do Bot Normal\n✅ IA com aprendizado\n✅ Base de conhecimento\n\nInteresse? Digite *quero contratar*"
                    },
                    {
                        "numero": "3",
                        "titulo": "Agente Financeiro",
                        "resposta": "💼 *Agente Financeiro*\n\nGestão financeira automatizada:\n\n💰 A partir de R$ 499/mês\n✅ Tudo do Bot IA\n✅ Controle financeiro\n✅ Relatórios automáticos\n\nInteresse? Digite *quero contratar*"
                    }
                ])
            },
            {
                "id": 2,
                "numero": "2",
                "titulo": "💬 Suporte",
                "descricao": "Canais de atendimento",
                "acao": "submenu",
                "submenu": json.dumps([
                    {
                        "numero": "1",
                        "titulo": "Horário de Atendimento",
                        "resposta": "⏰ *Horário de Atendimento*\n\n📅 Segunda a Sexta: 9h às 18h\n📅 Sábado: 9h às 13h\n❌ Domingo: Fechado\n\nFora do horário? Deixe sua mensagem!"
                    },
                    {
                        "numero": "2",
                        "titulo": "Falar com Atendente",
                        "resposta": "👤 Aguarde, você será transferido para um atendente humano em instantes..."
                    },
                    {
                        "numero": "3",
                        "titulo": "E-mail de Contato",
                        "resposta": "📧 *Contato por E-mail*\n\ncontato@kairix.com.br\nsuporte@kairix.com.br\n\nRespondemos em até 24h úteis!"
                    }
                ])
            },
            {
                "id": 3,
                "numero": "3",
                "titulo": "ℹ️ Sobre a Kairix",
                "descricao": "Informações da empresa",
                "acao": "resposta",
                "resposta": "🏢 *Sobre a Kairix*\n\nSomos especialistas em automação de atendimento via WhatsApp!\n\n✨ Nossa missão: Transformar o atendimento das empresas com tecnologia de ponta.\n\n🎯 +500 clientes atendidos\n⭐ 4.9/5.0 de satisfação\n🚀 Inovação constante\n\nQuer saber mais? Digite *quero contratar*"
            },
            {
                "id": 4,
                "numero": "4",
                "titulo": "👤 Falar com Atendente",
                "descricao": "Transferir para humano",
                "acao": "atendente"
            }
        ]

        # Carregar configuração atual ou criar nova
        config_atual = json.loads(pedido.configuracao_agente) if pedido.configuracao_agente else {}

        # Adicionar menu
        config_atual['menu'] = menu

        # Salvar
        pedido.configuracao_agente = json.dumps(config_atual, ensure_ascii=False)
        db.commit()

        print("✅ Menu criado com sucesso!")
        print(f"\n📊 Menu criado:")
        for opcao in menu:
            print(f"   {opcao['numero']}. {opcao['titulo']} ({opcao['acao']})")
            if opcao['acao'] == 'submenu':
                submenus = json.loads(opcao['submenu'])
                for sub in submenus:
                    print(f"      {sub['numero']}. {sub['titulo']}")

        return True

    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("🎨 CRIANDO MENU DE EXEMPLO")
    print("="*60)
    success = criar_menu_exemplo()
    if success:
        print("\n✅ PRONTO! Menu configurado no pedido #1")
    else:
        print("\n❌ Falhou ao criar menu")
    print("="*60)
