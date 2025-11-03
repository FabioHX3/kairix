"""
Router para gerenciamento da base de conhecimento do Agente IA
Upload, listagem e exclusão de documentos
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import os
import shutil

from database import get_db
import models
from services.rag_service import RAGService
from config_helper import get_qdrant_url, get_ollama_url, get_ollama_model, get_ollama_embeddings_model

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


def get_rag_service() -> RAGService:
    """Inicializa serviço RAG com configurações do sistema"""
    qdrant_url = get_qdrant_url()
    ollama_url = get_ollama_url()
    embeddings_model = get_ollama_embeddings_model()
    llm_model = get_ollama_model()

    return RAGService(
        qdrant_url=qdrant_url,
        ollama_url=ollama_url,
        embeddings_model=embeddings_model,
        llm_model=llm_model
    )


def get_storage_path(phone_number: str) -> Path:
    """Retorna caminho de armazenamento para um número de telefone"""
    storage_dir = Path("storage/knowledge_base") / phone_number
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


@router.post("/upload/{pedido_id}")
async def upload_document(
    pedido_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload de documento para base de conhecimento

    Args:
        pedido_id: ID do pedido
        file: Arquivo (PDF, DOCX, TXT)
    """
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Verificar se é plano com IA
    if pedido.plano.tipo != models.TipoPlano.AGENTE_IA:
        raise HTTPException(
            status_code=403,
            detail="Este plano não possui Agente IA"
        )

    # Buscar configuração do bot para pegar a instância
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_instance:
        raise HTTPException(
            status_code=400,
            detail="Instância do Evolution não configurada para este pedido"
        )

    # Usar nome da instância como identificador
    instance_name = config.evolution_instance

    # Verificar extensão do arquivo
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Formato não suportado. Use: {', '.join(allowed_extensions)}"
        )

    try:
        # Salvar arquivo
        storage_path = get_storage_path(instance_name)
        file_path = storage_path / file.filename

        # Salvar conteúdo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📁 Arquivo salvo: {file_path}")

        # Vetorizar documento
        rag_service = get_rag_service()
        chunks_count = rag_service.vectorize_document(
            phone_number=instance_name,
            file_path=str(file_path),
            metadata={
                "pedido_id": pedido_id,
                "uploaded_by": pedido.cliente.nome
            }
        )

        return {
            "success": True,
            "message": "Documento processado com sucesso",
            "filename": file.filename,
            "chunks_count": chunks_count,
            "instance_name": instance_name
        }

    except Exception as e:
        # Remover arquivo se houve erro
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(status_code=500, detail=f"Erro ao processar documento: {str(e)}")


@router.get("/list/{pedido_id}")
def list_documents(pedido_id: int, db: Session = Depends(get_db)):
    """Lista documentos da base de conhecimento"""
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_instance:
        return {"documents": [], "total": 0}

    # Usar nome da instância
    instance_name = config.evolution_instance

    # Listar arquivos no storage
    storage_path = get_storage_path(instance_name)
    documents = []

    if storage_path.exists():
        for file_path in storage_path.iterdir():
            if file_path.is_file():
                documents.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "uploaded_at": file_path.stat().st_mtime
                })

    # Listar documentos no Qdrant
    try:
        rag_service = get_rag_service()
        vectorized_docs = rag_service.list_documents(instance_name)
    except:
        vectorized_docs = []

    return {
        "documents": documents,
        "total": len(documents),
        "vectorized": vectorized_docs
    }


@router.get("/view/{pedido_id}/{filename}")
def view_document(pedido_id: int, filename: str, db: Session = Depends(get_db)):
    """Retorna o conteúdo de um documento"""
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_instance:
        return {"content": "Instância não configurada", "chunks": 0}

    # Usar nome da instância
    instance_name = config.evolution_instance

    # Buscar arquivo
    storage_path = get_storage_path(instance_name)
    file_path = storage_path / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    try:
        # Ler conteúdo do arquivo baseado na extensão
        file_extension = file_path.suffix.lower()

        if file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

        elif file_extension == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n\n"

        elif file_extension == '.docx':
            from docx import Document
            doc = Document(str(file_path))
            content = ""
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"

        else:
            content = "Formato não suportado para visualização"

        # Calcular número aproximado de chunks (cada chunk tem ~500 caracteres)
        chunks_count = len(content) // 500 + (1 if len(content) % 500 > 0 else 0)

        return {
            "content": content,
            "chunks": chunks_count,
            "filename": filename
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler documento: {str(e)}")


@router.delete("/delete/{pedido_id}/{filename}")
def delete_document(pedido_id: int, filename: str, db: Session = Depends(get_db)):
    """Deleta um documento da base de conhecimento"""
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_instance:
        raise HTTPException(status_code=400, detail="Instância do Evolution não configurada")

    # Usar nome da instância
    instance_name = config.evolution_instance

    # Deletar arquivo
    storage_path = get_storage_path(instance_name)
    file_path = storage_path / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    try:
        file_path.unlink()
        print(f"🗑️  Arquivo deletado: {file_path}")

        # TODO: Remover vetores específicos deste documento do Qdrant
        # Por enquanto, seria necessário reprocessar todos os outros documentos
        # ou implementar um sistema de tags para filtrar por arquivo

        return {
            "success": True,
            "message": f"Documento {filename} deletado",
            "note": "Os vetores permanecerão no Qdrant. Para limpeza completa, delete toda a base."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar documento: {str(e)}")


@router.delete("/clear/{pedido_id}")
def clear_knowledge_base(pedido_id: int, db: Session = Depends(get_db)):
    """Limpa completamente a base de conhecimento"""
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_instance:
        raise HTTPException(status_code=400, detail="Instância do Evolution não configurada")

    # Usar nome da instância
    instance_name = config.evolution_instance

    try:
        # Deletar todos os arquivos
        storage_path = get_storage_path(instance_name)
        if storage_path.exists():
            shutil.rmtree(storage_path)
            storage_path.mkdir(parents=True, exist_ok=True)

        # Deletar coleção do Qdrant
        rag_service = get_rag_service()
        rag_service.delete_knowledge_base(instance_name)

        return {
            "success": True,
            "message": "Base de conhecimento limpa completamente"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar base: {str(e)}")


from pydantic import BaseModel

class TestQuery(BaseModel):
    query: str

@router.post("/test/{pedido_id}")
def test_rag(pedido_id: int, data: TestQuery, db: Session = Depends(get_db)):
    """Testa o sistema RAG com uma pergunta"""
    # Buscar pedido
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_instance:
        raise HTTPException(status_code=400, detail="Instância do Evolution não configurada")

    # Usar nome da instância
    instance_name = config.evolution_instance

    try:
        # Processar pergunta
        rag_service = get_rag_service()
        answer = rag_service.process_question(instance_name, data.query)

        return {
            "success": True,
            "response": answer,
            "query": data.query
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar pergunta: {str(e)}")
