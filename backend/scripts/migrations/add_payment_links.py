"""
Script para adicionar links de pagamento do Kirvano aos planos existentes
"""
from database import SessionLocal
import models

# Links de pagamento fornecidos
payment_links = {
    # Agente Normal
    ("agente_normal", "mensal"): "https://pay.kirvano.com/05338928-c931-4f61-8702-9fad55f2b63e",
    ("agente_normal", "semestral"): "https://pay.kirvano.com/a5ad392c-5ad1-434a-945a-db50405c4b74",
    ("agente_normal", "anual"): "https://pay.kirvano.com/ed142ee4-5298-4cd6-bd39-eac3dd47afd6",

    # Agente com IA
    ("agente_ia", "mensal"): "https://pay.kirvano.com/f8b67a46-1074-4d48-a278-67f6eef0d32e",
    ("agente_ia", "semestral"): "https://pay.kirvano.com/862376f0-4ca0-4d34-a81b-5a6dbf6f28de",
    ("agente_ia", "anual"): "https://pay.kirvano.com/8fe7128a-4672-4907-896e-5dcaafd7148e",

    # Agente Financeiro
    ("agente_financeiro", "mensal"): "https://pay.kirvano.com/bad72101-8753-4333-9170-3244b24ab2a4",
    ("agente_financeiro", "semestral"): "https://pay.kirvano.com/158c1752-3e1f-4ed4-9f32-fe782b6d411d",
    ("agente_financeiro", "anual"): "https://pay.kirvano.com/bad72101-8753-4333-9170-3244b24ab2a4",
}

def main():
    db = SessionLocal()

    try:
        # Buscar todos os planos
        planos = db.query(models.Plano).all()

        print(f"📦 Encontrados {len(planos)} planos no banco de dados")
        print("\n" + "="*80)

        updated_count = 0

        for plano in planos:
            key = (plano.tipo, plano.periodo)

            if key in payment_links:
                link = payment_links[key]
                plano.link_pagamento = link
                updated_count += 1

                print(f"\n✅ Atualizado: {plano.nome}")
                print(f"   Tipo: {plano.tipo}")
                print(f"   Período: {plano.periodo}")
                print(f"   Link: {link}")
            else:
                print(f"\n⚠️  Sem link configurado: {plano.nome} ({plano.tipo} - {plano.periodo})")

        # Salvar alterações
        db.commit()

        print("\n" + "="*80)
        print(f"\n🎉 Concluído! {updated_count} planos atualizados com sucesso!")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
