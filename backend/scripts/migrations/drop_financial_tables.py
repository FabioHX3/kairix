#!/usr/bin/env python3
"""
Script para remover as tabelas financeiras do banco de dados
"""
from sqlalchemy import text
from database import engine

def drop_financial_tables():
    """Remove as tabelas categorias_financeiras e transacoes_financeiras"""
    try:
        with engine.connect() as connection:
            # Dropar tabelas financeiras (ordem importa por causa das foreign keys)
            connection.execute(text("DROP TABLE IF EXISTS transacoes_financeiras CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS categorias_financeiras CASCADE"))
            connection.commit()
            print("✅ Tabelas financeiras removidas com sucesso!")
            print("   - transacoes_financeiras")
            print("   - categorias_financeiras")
    except Exception as e:
        print(f"❌ Erro ao remover tabelas: {e}")

if __name__ == "__main__":
    print("🗑️  Removendo tabelas financeiras...")
    drop_financial_tables()
