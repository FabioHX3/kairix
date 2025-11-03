#!/bin/bash
# Script para iniciar o verificador automático de vencimentos

echo "🚀 Iniciando Verificador Automático de Vencimentos..."
echo ""

# Ir para o diretório do backend
cd /mnt/c/PROJETOS/kairix/backend

# Verificar se o backend está rodando
if ! curl -s http://localhost:8012/api/admin/dashboard > /dev/null 2>&1; then
    echo "⚠️  AVISO: Backend não está respondendo em http://localhost:8012"
    echo "   Certifique-se de iniciar o backend primeiro!"
    echo ""
    read -p "Deseja continuar mesmo assim? (s/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Cancelado."
        exit 1
    fi
fi

# Matar qualquer verificador anterior
pkill -f "verificador_vencimentos.py" 2>/dev/null && echo "✅ Verificador anterior finalizado"

# Iniciar o verificador em background
nohup /mnt/c/PROJETOS/kairix/backend/venv/bin/python verificador_vencimentos.py > /tmp/kairix-verificador-output.log 2>&1 &

VERIFICADOR_PID=$!

echo ""
echo "✅ Verificador iniciado com sucesso!"
echo ""
echo "📋 Informações:"
echo "   • PID: $VERIFICADOR_PID"
echo "   • Log: /tmp/kairix-verificador.log"
echo "   • Output: /tmp/kairix-verificador-output.log"
echo "   • Horário: Todo dia às 02:00"
echo ""
echo "📝 Comandos úteis:"
echo "   • Ver log ao vivo:  tail -f /tmp/kairix-verificador.log"
echo "   • Parar verificador: pkill -f 'verificador_vencimentos.py'"
echo "   • Ver status:        ps aux | grep verificador_vencimentos"
echo ""
