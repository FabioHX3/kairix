"""
Script para popular o banco de dados com os planos iniciais
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import sys

# DROPAR todas as tabelas e recriar
print("🗑️  Dropando tabelas antigas...")
models.Base.metadata.drop_all(bind=engine)

print("📦 Criando tabelas novas em português...")
models.Base.metadata.create_all(bind=engine)

def populate_plans():
    db = SessionLocal()

    try:
        plans_data = [
            # ============= AGENTE NORMAL =============
            {
                "nome": "Starter",
                "tipo": models.TipoPlano.AGENTE_NORMAL,
                "periodo": models.PeriodoPlano.MENSAL,
                "preco": 32.00,
                "preco_antigo": 97.00,
                "descricao": "Perfeito para começar a automatizar",
                "destaque": False
            },
            {
                "nome": "Professional",
                "tipo": models.TipoPlano.AGENTE_NORMAL,
                "periodo": models.PeriodoPlano.SEMESTRAL,
                "preco": 164.00,
                "preco_antigo": 492.00,
                "descricao": "Apenas R$ 27/mês - Pagamento semestral",
                "destaque": True
            },
            {
                "nome": "Enterprise",
                "tipo": models.TipoPlano.AGENTE_NORMAL,
                "periodo": models.PeriodoPlano.ANUAL,
                "preco": 291.00,
                "preco_antigo": 873.00,
                "descricao": "Apenas R$ 24/mês - Pagamento anual",
                "destaque": False
            },

            # ============= AGENTE COM IA =============
            {
                "nome": "IA Essencial",
                "tipo": models.TipoPlano.AGENTE_IA,
                "periodo": models.PeriodoPlano.MENSAL,
                "preco": 64.00,
                "preco_antigo": 194.00,
                "descricao": "Ideal para começar com IA",
                "destaque": False
            },
            {
                "nome": "IA Professional",
                "tipo": models.TipoPlano.AGENTE_IA,
                "periodo": models.PeriodoPlano.SEMESTRAL,
                "preco": 345.00,
                "preco_antigo": 384.00,
                "descricao": "Apenas R$ 57,50/mês - Pagamento semestral",
                "destaque": True
            },
            {
                "nome": "IA Enterprise",
                "tipo": models.TipoPlano.AGENTE_IA,
                "periodo": models.PeriodoPlano.ANUAL,
                "preco": 614.00,
                "preco_antigo": 768.00,
                "descricao": "Apenas R$ 51/mês - Pagamento anual",
                "destaque": False
            },

            # ============= AGENTE FINANCEIRO =============
            {
                "nome": "Básico",
                "tipo": models.TipoPlano.AGENTE_FINANCEIRO,
                "periodo": models.PeriodoPlano.MENSAL,
                "preco": 147.00,
                "preco_antigo": None,
                "descricao": "Para quem está começando",
                "destaque": False
            },
            {
                "nome": "Profissional",
                "tipo": models.TipoPlano.AGENTE_FINANCEIRO,
                "periodo": models.PeriodoPlano.SEMESTRAL,
                "preco": 749.00,
                "preco_antigo": None,
                "descricao": "R$ 125/mês cobrado semestralmente (15% OFF)",
                "destaque": True
            },
            {
                "nome": "Enterprise",
                "tipo": models.TipoPlano.AGENTE_FINANCEIRO,
                "periodo": models.PeriodoPlano.ANUAL,
                "preco": 1323.00,
                "preco_antigo": None,
                "descricao": "R$ 110/mês cobrado anualmente (25% OFF)",
                "destaque": False
            },
        ]

        created_count = 0
        for plan_data in plans_data:
            plan = models.Plano(**plan_data)
            db.add(plan)
            created_count += 1

        db.commit()
        print(f"✅ {created_count} planos criados com sucesso!")

        # Listar planos criados
        print("\n📋 Planos cadastrados:")
        plans = db.query(models.Plano).all()
        for plan in plans:
            featured = "⭐" if plan.destaque else "  "
            print(f"{featured} ID: {plan.id:2d} | {plan.nome:20s} | {plan.tipo.value:20s} | {plan.periodo.value:10s} | R$ {plan.preco:.2f}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar planos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Recriando banco de dados com estrutura em português...\n")
    populate_plans()
    print("\n✅ Banco de dados pronto!")
