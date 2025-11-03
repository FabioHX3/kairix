"""
Script para criar a tabela de métricas
"""
import models
from database import engine

print("📊 Criando tabela de métricas...")
models.Base.metadata.create_all(bind=engine)
print("✅ Tabela criada com sucesso!")
