#!/bin/bash

echo "🚀 Iniciando Kairix Backend..."
echo ""

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Verificar se os planos já foram populados
echo ""
echo "⚙️  Deseja popular o banco com os planos iniciais? (s/n)"
read -r response
if [[ "$response" == "s" ]]; then
    echo "📋 Populando banco de dados..."
    python populate_plans.py
fi

# Iniciar servidor
echo ""
echo "✅ Iniciando servidor em http://localhost:8012"
echo "📖 Documentação disponível em http://localhost:8012/docs"
echo ""
python main.py
