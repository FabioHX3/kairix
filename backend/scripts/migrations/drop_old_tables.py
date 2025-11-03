"""
Script para remover tabelas antigas em inglês do banco de dados
"""
from sqlalchemy import create_engine, MetaData, inspect, text
from database import engine
import sys

def drop_old_tables():
    """Remove tabelas antigas em inglês do banco"""

    # Nomes das tabelas antigas em inglês que devem ser removidas
    old_tables = [
        'plans',
        'clients',
        'orders',
        'order_status_history'
    ]

    # Inspecionar banco de dados
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    print("📋 Tabelas existentes no banco:")
    for table in existing_tables:
        print(f"  - {table}")

    print("\n🗑️  Removendo tabelas antigas em inglês...")

    with engine.connect() as connection:
        for table_name in old_tables:
            if table_name in existing_tables:
                try:
                    # Dropar tabela
                    connection.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
                    connection.commit()
                    print(f"  ✅ Tabela '{table_name}' removida com sucesso")
                except Exception as e:
                    print(f"  ❌ Erro ao remover tabela '{table_name}': {e}")
            else:
                print(f"  ⏭️  Tabela '{table_name}' não existe (já foi removida)")

    # Listar tabelas restantes
    inspector = inspect(engine)
    remaining_tables = inspector.get_table_names()

    print("\n📋 Tabelas restantes no banco:")
    for table in remaining_tables:
        print(f"  - {table}")

    print("\n✅ Limpeza concluída!")

if __name__ == "__main__":
    print("🚀 Iniciando limpeza de tabelas antigas...\n")
    drop_old_tables()
