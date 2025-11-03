#!/usr/bin/env python3
"""
Script para criar as tabelas de conversas, mensagens e métricas
"""
from database import engine
from models import Base
from sqlalchemy import text

def create_tables():
    """Cria as tabelas de conversas no banco"""
    try:
        # Dropar tabela metricas_diarias antiga (com cliente_id)
        print("🗑️  Removendo tabela metricas_diarias antiga...")
        with engine.connect() as connection:
            connection.execute(text("DROP TABLE IF EXISTS metricas_diarias CASCADE"))
            connection.commit()
        print("✅ Tabela antiga removida!")

        # Criar todas as tabelas
        print("📦 Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        print("   - conversas")
        print("   - mensagens")
        print("   - metricas_diarias (atualizada)")

    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    print("🚀 Criando tabelas do sistema de conversas...")
    create_tables()
