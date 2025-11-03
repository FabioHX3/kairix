"""
Serviço de RAG (Retrieval-Augmented Generation)
Vetorização de documentos e busca semântica usando Qdrant + Ollama
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document
import chardet
from config_helper import (
    get_rag_chunk_size,
    get_rag_chunk_overlap,
    get_rag_search_limit,
    get_rag_num_predict,
    get_rag_temperature,
    get_rag_top_p
)


class RAGService:
    def __init__(self, qdrant_url: str, ollama_url: str, embeddings_model: str, llm_model: str):
        self.qdrant_url = qdrant_url
        self.ollama_url = ollama_url
        self.embeddings_model = embeddings_model
        self.llm_model = llm_model
        self.qdrant_client = QdrantClient(url=qdrant_url)

        # Buscar configurações do banco
        chunk_size = get_rag_chunk_size()
        chunk_overlap = get_rag_chunk_overlap()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def get_collection_name(self, phone_number: str) -> str:
        """Retorna nome da coleção para um número de telefone"""
        return f"kb_{phone_number}"

    def create_collection_if_not_exists(self, phone_number: str, vector_size: int = 384):
        """Cria coleção no Qdrant se não existir"""
        collection_name = self.get_collection_name(phone_number)

        try:
            collections = self.qdrant_client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if not exists:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
                )
                print(f"✅ Coleção criada: {collection_name}")
            else:
                print(f"ℹ️  Coleção já existe: {collection_name}")
        except Exception as e:
            print(f"❌ Erro ao criar coleção: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """Gera embedding usando Ollama"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embeddings_model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"❌ Erro ao gerar embedding: {e}")
            raise

    def extract_text_from_file(self, file_path: str) -> str:
        """Extrai texto de PDF, DOCX ou TXT"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        try:
            if extension == '.pdf':
                reader = PdfReader(file_path)
                text = "\n".join([page.extract_text() for page in reader.pages])
                return text

            elif extension == '.docx':
                doc = Document(file_path)
                text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                return text

            elif extension == '.txt':
                # Detectar encoding
                with open(file_path, 'rb') as f:
                    raw = f.read()
                    detected = chardet.detect(raw)
                    encoding = detected['encoding'] or 'utf-8'

                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()

            else:
                raise ValueError(f"Formato não suportado: {extension}")

        except Exception as e:
            print(f"❌ Erro ao extrair texto de {file_path}: {e}")
            raise

    def vectorize_document(self, phone_number: str, file_path: str, metadata: Optional[Dict] = None) -> int:
        """Vetoriza um documento e armazena no Qdrant"""
        print(f"📄 Vetorizando documento: {file_path}")

        # Extrair texto
        text = self.extract_text_from_file(file_path)

        # Dividir em chunks
        chunks = self.text_splitter.split_text(text)
        print(f"📝 Documento dividido em {len(chunks)} chunks")

        # Criar coleção se não existir
        if chunks:
            # Gerar embedding de exemplo para descobrir dimensão
            sample_embedding = self.generate_embedding(chunks[0])
            self.create_collection_if_not_exists(phone_number, vector_size=len(sample_embedding))

        collection_name = self.get_collection_name(phone_number)

        # Vetorizar e armazenar chunks
        points = []
        for i, chunk in enumerate(chunks):
            embedding = self.generate_embedding(chunk)

            point_metadata = {
                "text": chunk,
                "file_name": Path(file_path).name,
                "chunk_index": i,
                **(metadata or {})
            }

            points.append(PointStruct(
                id=hash(f"{phone_number}_{Path(file_path).name}_{i}") & 0x7FFFFFFF,
                vector=embedding,
                payload=point_metadata
            ))

        # Inserir no Qdrant
        if points:
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            print(f"✅ {len(points)} chunks vetorizados e armazenados")

        return len(chunks)

    def _search_by_text(self, phone_number: str, query: str, storage_path: Path) -> List[Dict]:
        """Busca textual direta nos arquivos (mais rápida para termos específicos)"""
        try:
            import re

            results = []
            query_lower = query.lower()

            # Extrair palavras-chave da query (remover stopwords)
            stopwords = {'qual', 'quais', 'como', 'onde', 'quando', 'o', 'a', 'os', 'as', 'de', 'do', 'da', 'encontre', 'busque', 'mostre', 'liste'}
            keywords = [w for w in query_lower.split() if w not in stopwords and len(w) > 2]

            # Se não há keywords, retornar vazio
            if not keywords:
                return []

            # Buscar em todos os arquivos da pasta
            if not storage_path.exists():
                return []

            for file_path in storage_path.iterdir():
                if not file_path.is_file():
                    continue

                try:
                    # Extrair texto do arquivo
                    text = self.extract_text_from_file(str(file_path))
                    text_lower = text.lower()

                    # Normalizar espaços
                    text_norm = re.sub(r'\s+', ' ', text_lower)
                    query_norm = re.sub(r'\s+', ' ', query_lower)

                    # Buscar por frase exata ou palavras-chave
                    found = False
                    search_pos = -1

                    if query_norm in text_norm:
                        found = True
                        search_pos = text_norm.find(query_norm)
                    else:
                        # Buscar por combinações de 2 palavras
                        for i in range(len(keywords)-1):
                            bigram = f"{keywords[i]} {keywords[i+1]}"
                            if bigram in text_norm:
                                found = True
                                search_pos = text_norm.find(bigram)
                                break

                        # Se não encontrou, buscar palavra individual
                        if not found:
                            for keyword in keywords:
                                if keyword in text_norm:
                                    found = True
                                    search_pos = text_norm.find(keyword)
                                    break

                    if found and search_pos >= 0:
                        # Extrair contexto
                        start = max(0, search_pos - 500)
                        end = min(len(text), search_pos + 1500)
                        context = text[start:end]

                        results.append({
                            "text": context,
                            "score": 0.95,
                            "file_name": file_path.name,
                            "metadata": {
                                "source": "text_search",
                                "file_name": file_path.name
                            }
                        })
                except Exception as e:
                    print(f"⚠️ Erro ao buscar em {file_path.name}: {e}")
                    continue

            if results:
                print(f"✅ Busca textual RÁPIDA: {len(results)} arquivo(s)")
            return results[:10]

        except Exception as e:
            print(f"❌ Erro na busca textual: {e}")
            return []

    def search(self, phone_number: str, query: str, limit: int = 50) -> List[Dict]:
        """Busca híbrida: textual (rápida) + semântica (precisa)"""
        collection_name = self.get_collection_name(phone_number)

        # Tentar busca textual primeiro para queries específicas
        storage_path = Path("storage/knowledge_base") / phone_number

        # Detectar se é pergunta específica que pode se beneficiar de busca textual
        query_lower = query.lower()
        is_specific_query = any(term in query_lower for term in [
            'qual', 'quais', 'como', 'onde', 'quando', 'quanto', 'quem',
            'mostre', 'liste', 'busque', 'encontre', 'procure'
        ])

        text_results = []
        if is_specific_query and len(query.split()) <= 10:
            print("🔍 Tentando busca textual rápida primeiro...")
            text_results = self._search_by_text(phone_number, query, storage_path)

            # Se encontrou resultados bons na busca textual, retornar
            if len(text_results) >= 3:
                print(f"✅ Busca textual retornou {len(text_results)} resultados")
                return text_results

        try:
            # Verificar se coleção existe
            collections = self.qdrant_client.get_collections().collections
            exists = any(c.name == collection_name for c in collections)

            if not exists:
                print(f"⚠️  Coleção não encontrada: {collection_name}")
                return text_results  # Retornar resultados textuais se houver

            # Gerar embedding da query
            query_embedding = self.generate_embedding(query)

            # Buscar no Qdrant com limite maior
            print(f"🔍 Buscando {limit} chunks no Qdrant...")
            results = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit
            )

            # Formatar resultados
            search_results = []
            for result in results:
                search_results.append({
                    "text": result.payload.get("text", ""),
                    "score": result.score,
                    "file_name": result.payload.get("file_name", ""),
                    "metadata": result.payload
                })

            # Combinar resultados textuais (prioridade) com vetoriais
            combined_results = text_results + search_results

            # Remover duplicatas mantendo os de maior score
            seen_texts = set()
            unique_results = []
            for result in combined_results:
                text_hash = hash(result["text"][:100])  # Hash dos primeiros 100 chars
                if text_hash not in seen_texts:
                    seen_texts.add(text_hash)
                    unique_results.append(result)

            return unique_results[:limit]

        except Exception as e:
            print(f"❌ Erro na busca vetorial: {e}")
            return text_results  # Retornar resultados textuais como fallback

    def generate_response(self, phone_number: str, question: str, context_results: List[Dict]) -> str:
        """Gera resposta usando LLM com contexto RAG"""
        # Montar contexto
        context = "\n\n".join([
            f"[Fonte: {r['file_name']}]\n{r['text']}"
            for r in context_results
        ])

        # Detectar se usuário quer apenas tópicos/títulos (sem descrições)
        question_lower = question.lower()
        apenas_topicos = any(keyword in question_lower for keyword in [
            'apenas', 'só', 'somente', 'quais os', 'quais são os', 'liste os', 'lista de'
        ]) and any(keyword in question_lower for keyword in [
            'tópico', 'topico', 'título', 'titulo', 'item', 'assunto'
        ])

        # Prompt para o LLM
        if apenas_topicos:
            prompt = f"""Você é um assistente inteligente que responde perguntas baseado nas informações fornecidas.

CONTEXTO (informações da empresa):
{context}

PERGUNTA DO CLIENTE:
{question}

INSTRUÇÕES ESPECIAIS:
- O cliente pediu APENAS OS TÓPICOS/TÍTULOS, SEM DESCRIÇÕES
- Liste TODOS os tópicos/títulos encontrados no contexto
- Use formato de lista numerada (1. 2. 3. etc)
- NÃO adicione descrições, explicações ou detalhes
- Liste APENAS os nomes/títulos, um por linha
- Seja completo e liste TODOS os tópicos que encontrar
- Use português do Brasil

RESPOSTA (apenas títulos):"""
        else:
            prompt = f"""Você é um assistente inteligente que responde perguntas baseado nas informações fornecidas.

CONTEXTO (informações da empresa):
{context}

PERGUNTA DO CLIENTE:
{question}

INSTRUÇÕES:
- Responda a pergunta usando APENAS as informações do contexto acima
- Se a pergunta pede uma LISTA de itens/tópicos, liste TODOS os itens encontrados no contexto
- Se a informação não estiver no contexto, diga: "Não tenho essa informação disponível. Por favor, entre em contato com um atendente."
- Seja educado, claro e completo
- Não invente informações
- Use português do Brasil
- Quando houver múltiplos tópicos, liste todos com seus títulos e descrições

RESPOSTA:"""

        try:
            # Buscar configurações do banco
            num_predict = get_rag_num_predict()
            temperature = get_rag_temperature()
            top_p = get_rag_top_p()

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": num_predict,
                        "temperature": temperature,
                        "top_p": top_p
                    }
                },
                timeout=120  # Aumentado para 120 segundos (queries complexas)
            )
            response.raise_for_status()
            answer = response.json().get("response", "").strip()

            # Adicionar mensagem para falar com atendente
            answer += "\n\n_Para falar com um atendente humano, digite *atendente*._"

            return answer

        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua pergunta. Por favor, entre em contato com um atendente."

    def process_question(self, phone_number: str, question: str) -> str:
        """Pipeline completo: busca + geração de resposta"""
        print(f"🤔 Processando pergunta: {question}")

        # Buscar contexto relevante (usando configuração do banco)
        search_limit = get_rag_search_limit()
        results = self.search(phone_number, question, limit=search_limit)

        if not results:
            return "Ainda não tenho informações suficientes para responder. Por favor, entre em contato com um atendente digitando *atendente*."

        print(f"📚 Encontrados {len(results)} documentos relevantes")

        # Gerar resposta
        answer = self.generate_response(phone_number, question, results)

        return answer

    def delete_knowledge_base(self, phone_number: str):
        """Deleta toda a base de conhecimento de um número"""
        collection_name = self.get_collection_name(phone_number)

        try:
            self.qdrant_client.delete_collection(collection_name)
            print(f"🗑️  Base de conhecimento deletada: {collection_name}")
        except Exception as e:
            print(f"⚠️  Erro ao deletar coleção: {e}")

    def list_documents(self, phone_number: str) -> List[str]:
        """Lista documentos vetorizados para um número"""
        collection_name = self.get_collection_name(phone_number)

        try:
            # Buscar todos os pontos
            result = self.qdrant_client.scroll(
                collection_name=collection_name,
                limit=1000
            )

            # Extrair nomes de arquivos únicos
            file_names = set()
            for point in result[0]:
                if "file_name" in point.payload:
                    file_names.add(point.payload["file_name"])

            return sorted(list(file_names))

        except Exception as e:
            print(f"❌ Erro ao listar documentos: {e}")
            return []
