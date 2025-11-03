#!/bin/bash
echo "🔍 Monitorando webhooks do Evolution..."
echo "Aguardando mensagens..."
echo "================================"
echo ""
tail -f /proc/$(cat /tmp/server.pid)/fd/1 | grep --line-buffered -E "(WEBHOOK|🔔|📦|Salvando|salva com ID)"
