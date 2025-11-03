#!/bin/bash

echo "================================"
echo "🚀 INICIANDO LOCALTUNNEL"
echo "================================"
echo ""
echo "Aguarde..."
echo ""

# Matar processos antigos
pkill -9 -f "node.*localtunnel" 2>/dev/null

# Iniciar localtunnel
npx localtunnel --port 8012

# Se o comando acima não funcionar, tente:
# lt --port 8012
