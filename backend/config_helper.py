"""
Helper para buscar configurações do sistema.
Busca do banco de dados com fallback para .env
"""
import os
from sqlalchemy.orm import Session
from typing import Optional
import models
import crud
from database import SessionLocal


_config_cache = None
_cache_timestamp = None


def get_system_config(db: Session = None, use_cache: bool = True) -> models.ConfiguracaoSistema:
    """
    Busca configurações do sistema do banco de dados.
    Usa cache para evitar múltiplas consultas.
    Fallback para .env se banco estiver vazio.
    """
    global _config_cache, _cache_timestamp

    # Se tem cache e solicitou uso de cache, retorna do cache
    if use_cache and _config_cache is not None:
        return _config_cache

    # Criar sessão se não foi fornecida
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        # Buscar configuração do banco
        config = crud.get_configuracao_sistema(db)

        # Atualizar cache
        _config_cache = config

        return config
    finally:
        if close_session:
            db.close()


def clear_config_cache():
    """Limpa o cache de configurações"""
    global _config_cache
    _config_cache = None


# Funções específicas para cada configuração com fallback para .env
def get_evolution_api_url(db: Session = None) -> str:
    """Retorna a URL da Evolution API"""
    config = get_system_config(db)
    return config.evolution_api_url or os.getenv("EVOLUTION_API_URL", "http://localhost:8055")


def get_evolution_api_key(db: Session = None) -> str:
    """Retorna a API Key da Evolution API"""
    config = get_system_config(db)
    return config.evolution_api_key or os.getenv("EVOLUTION_API_KEY", "")


def get_ollama_url(db: Session = None) -> str:
    """Retorna a URL do Ollama"""
    config = get_system_config(db)
    return config.ollama_url or os.getenv("OLLAMA_URL", "http://localhost:11434")


def get_ollama_model(db: Session = None) -> str:
    """Retorna o modelo do Ollama"""
    config = get_system_config(db)
    return config.ollama_model or os.getenv("OLLAMA_MODEL", "llama3")


def get_ollama_embeddings_model(db: Session = None) -> str:
    """Retorna o modelo de embeddings do Ollama"""
    config = get_system_config(db)
    return config.ollama_embeddings_model or os.getenv("OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text")


def get_qdrant_url(db: Session = None) -> str:
    """Retorna a URL do Qdrant"""
    config = get_system_config(db)
    return config.qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")


def get_qdrant_api_key(db: Session = None) -> Optional[str]:
    """Retorna a API Key do Qdrant (opcional)"""
    config = get_system_config(db)
    return config.qdrant_api_key or os.getenv("QDRANT_API_KEY")


def get_qdrant_collection(db: Session = None) -> str:
    """Retorna o nome da coleção do Qdrant"""
    config = get_system_config(db)
    return config.qdrant_collection or os.getenv("QDRANT_COLLECTION", "kairix")


def get_rag_chunk_size(db: Session = None) -> int:
    """Retorna o tamanho dos chunks para RAG"""
    config = get_system_config(db)
    return config.rag_chunk_size or int(os.getenv("RAG_CHUNK_SIZE", "1500"))


def get_rag_chunk_overlap(db: Session = None) -> int:
    """Retorna a sobreposição dos chunks para RAG"""
    config = get_system_config(db)
    return config.rag_chunk_overlap or int(os.getenv("RAG_CHUNK_OVERLAP", "200"))


def get_rag_search_limit(db: Session = None) -> int:
    """Retorna o número de documentos recuperados na busca RAG"""
    config = get_system_config(db)
    return config.rag_search_limit or int(os.getenv("RAG_SEARCH_LIMIT", "5"))


def get_rag_num_predict(db: Session = None) -> int:
    """Retorna o número máximo de tokens na resposta RAG"""
    config = get_system_config(db)
    return config.rag_num_predict or int(os.getenv("RAG_NUM_PREDICT", "800"))


def get_rag_temperature(db: Session = None) -> float:
    """Retorna a temperatura (criatividade) do modelo RAG"""
    config = get_system_config(db)
    return config.rag_temperature or float(os.getenv("RAG_TEMPERATURE", "0.6"))


def get_rag_top_p(db: Session = None) -> float:
    """Retorna o top_p (nucleus sampling) do modelo RAG"""
    config = get_system_config(db)
    return config.rag_top_p or float(os.getenv("RAG_TOP_P", "0.9"))
