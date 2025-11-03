#!/usr/bin/env python3
"""
Script para remover a tabela historico_status_pedidos do banco de dados
"""
from sqlalchemy import text
from database import engine

def drop_historico_status_table():
    """Remove a tabela historico_status_pedidos"""
    try:
        with engine.connect() as connection:
            # Dropar a tabela
            connection.execute(text("DROP TABLE IF EXISTS historico_status_pedidos CASCADE"))
            connection.commit()
            print("✅ Tabela 'historico_status_pedidos' removida com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao remover tabela: {e}")

if __name__ == "__main__":
    print("🗑️  Removendo tabela historico_status_pedidos...")
    drop_historico_status_table()
