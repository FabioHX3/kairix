"""
Script para migrar configurações do .env para o banco de dados
"""
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import models
import schemas
import crud
from database import engine, SessionLocal

# Carregar variáveis de ambiente
load_dotenv()

def migrar_configuracoes():
    """Migra configurações do .env para o banco de dados"""

    # Criar tabelas se não existirem
    models.Base.metadata.create_all(bind=engine)

    # Criar sessão
    db: Session = SessionLocal()

    try:
        # Buscar ou criar configuração
        config = crud.get_configuracao_sistema(db)

        print("🔄 Migrando configurações do .env para o banco de dados...")

        # Preparar dados de atualização
        config_data = schemas.ConfiguracaoSistemaAtualizar(
            # Evolution API (configurações globais)
            evolution_api_url=os.getenv("EVOLUTION_API_URL"),
            evolution_api_key=os.getenv("EVOLUTION_API_KEY"),

            # Qdrant (se existir no .env)
            qdrant_url=os.getenv("QDRANT_URL"),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            qdrant_collection=os.getenv("QDRANT_COLLECTION", "kairix"),

            # Ollama (IA Local)
            ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3"),
            ollama_embeddings_model=os.getenv("OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text"),
        )

        # Atualizar configurações
        config = crud.update_configuracao_sistema(db, config_data)

        print("✅ Configurações migradas com sucesso!")
        print("\n📋 Configurações salvas:")
        print(f"  • Evolution API URL: {config.evolution_api_url}")
        print(f"  • Ollama URL: {config.ollama_url}")
        print(f"  • Ollama Model (Chat): {config.ollama_model}")
        print(f"  • Ollama Model (Embeddings): {config.ollama_embeddings_model}")
        print(f"  • Qdrant URL: {config.qdrant_url}")
        print(f"  • Qdrant Collection: {config.qdrant_collection}")

        return config

    except Exception as e:
        print(f"❌ Erro ao migrar configurações: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrar_configuracoes()
