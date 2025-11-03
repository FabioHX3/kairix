#!/bin/bash
#
# Script de instalação dos serviços de IA para o Kairix
# - Ollama (LLM local)
# - Qdrant (banco vetorial)
#

set -e

echo "🤖 ====================================="
echo "   Instalação de Serviços de IA Kairix"
echo "====================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está rodando em WSL
if grep -qi microsoft /proc/version; then
    echo -e "${YELLOW}⚠️  Detectado WSL (Windows Subsystem for Linux)${NC}"
    IS_WSL=true
else
    IS_WSL=false
fi

# 1. INSTALAR OLLAMA
echo ""
echo "📦 1/3: Instalando Ollama..."
echo "-----------------------------------"

if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama já está instalado${NC}"
else
    echo "📥 Baixando e instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Ollama instalado com sucesso${NC}"
    else
        echo -e "${RED}❌ Erro ao instalar Ollama${NC}"
        exit 1
    fi
fi

# Iniciar serviço do Ollama
echo "🚀 Iniciando serviço do Ollama..."
if $IS_WSL; then
    # No WSL, rodar em background
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo -e "${GREEN}✅ Ollama iniciado em background${NC}"
else
    # Em Linux normal, usar systemctl
    sudo systemctl start ollama 2>/dev/null || {
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
    }
    echo -e "${GREEN}✅ Ollama serviço iniciado${NC}"
fi

# Baixar modelo LLM (llama3)
echo "📥 Baixando modelo LLM (llama3)..."
echo "⏳ Isso pode demorar alguns minutos..."
ollama pull llama3

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Modelo llama3 baixado${NC}"
else
    echo -e "${RED}❌ Erro ao baixar modelo${NC}"
fi

# Baixar modelo de embeddings
echo "📥 Baixando modelo de embeddings (nomic-embed-text)..."
ollama pull nomic-embed-text

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Modelo nomic-embed-text baixado${NC}"
else
    echo -e "${RED}❌ Erro ao baixar modelo de embeddings${NC}"
fi

# 2. INSTALAR DOCKER (se necessário)
echo ""
echo "🐳 2/3: Verificando Docker..."
echo "-----------------------------------"

if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker já está instalado${NC}"
else
    echo "📥 Instalando Docker..."

    if $IS_WSL; then
        echo -e "${YELLOW}⚠️  Em WSL, recomendamos instalar Docker Desktop for Windows${NC}"
        echo "Visite: https://www.docker.com/products/docker-desktop"
        read -p "Pressione Enter para continuar (assumindo que Docker está disponível)..."
    else
        # Instalar Docker no Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        echo -e "${GREEN}✅ Docker instalado${NC}"
    fi
fi

# 3. INSTALAR E INICIAR QDRANT
echo ""
echo "🗄️  3/3: Instalando Qdrant (banco vetorial)..."
echo "-----------------------------------"

# Verificar se container já existe
if docker ps -a | grep -q qdrant; then
    echo "🔄 Container Qdrant já existe"

    # Verificar se está rodando
    if docker ps | grep -q qdrant; then
        echo -e "${GREEN}✅ Qdrant já está rodando${NC}"
    else
        echo "🚀 Iniciando container Qdrant..."
        docker start qdrant
        echo -e "${GREEN}✅ Qdrant iniciado${NC}"
    fi
else
    echo "📥 Criando container Qdrant..."
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v qdrant_storage:/qdrant/storage \
        qdrant/qdrant

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Qdrant instalado e rodando${NC}"
    else
        echo -e "${RED}❌ Erro ao criar container Qdrant${NC}"
        exit 1
    fi
fi

# Aguardar Qdrant inicializar
echo "⏳ Aguardando Qdrant inicializar..."
sleep 5

# VERIFICAÇÕES FINAIS
echo ""
echo "🔍 Verificando serviços..."
echo "-----------------------------------"

# Verificar Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama: ONLINE (http://localhost:11434)${NC}"
else
    echo -e "${RED}❌ Ollama: OFFLINE${NC}"
fi

# Verificar Qdrant
if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant: ONLINE (http://localhost:6333)${NC}"
else
    echo -e "${RED}❌ Qdrant: OFFLINE${NC}"
fi

# CONCLUSÃO
echo ""
echo "🎉 ====================================="
echo "   Instalação Concluída!"
echo "====================================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Acesse o painel admin: http://172.23.107.238:8012/admin"
echo "2. Configure os serviços de IA:"
echo "   - Ollama URL: http://localhost:11434"
echo "   - Ollama Model: llama3"
echo "   - Ollama Embeddings: nomic-embed-text"
echo "   - Qdrant URL: http://localhost:6333"
echo ""
echo "3. No painel do cliente, faça upload de documentos"
echo "4. Teste o Agente IA pelo WhatsApp!"
echo ""
echo "🔗 Links úteis:"
echo "   - Ollama: http://localhost:11434"
echo "   - Qdrant: http://localhost:6333/dashboard"
echo ""
echo -e "${GREEN}✅ Tudo pronto para usar o Agente IA!${NC}"
echo ""
