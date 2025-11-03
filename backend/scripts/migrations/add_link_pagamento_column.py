"""
Script de migração para adicionar coluna link_pagamento na tabela planos
"""
from database import engine
from sqlalchemy import text

def add_column():
    try:
        with engine.connect() as conn:
            # Adicionar coluna link_pagamento
            conn.execute(text("""
                ALTER TABLE planos
                ADD COLUMN IF NOT EXISTS link_pagamento VARCHAR(500);
            """))
            conn.commit()
            print("✅ Coluna 'link_pagamento' adicionada com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("ℹ️  A coluna já existe, continuando...")

if __name__ == "__main__":
    add_column()
