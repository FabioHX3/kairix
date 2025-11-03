#!/usr/bin/env python3
"""
Script automático para verificar vencimentos de planos diariamente.
Executa em background e chama o endpoint de verificação.
"""
import schedule
import time
import requests
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/kairix-verificador.log'),
        logging.StreamHandler()
    ]
)

API_URL = "http://localhost:8012/api/admin/verificar-vencimentos"

def verificar_vencimentos():
    """Executa a verificação de vencimentos"""
    try:
        logging.info("=" * 60)
        logging.info("Iniciando verificação de vencimentos...")

        response = requests.get(API_URL, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # Log dos resultados
            logging.info(f"✅ Verificação concluída com sucesso!")
            logging.info(f"   • Clientes desativados: {data['total_desativados']}")
            logging.info(f"   • Alertas de vencimento: {data['total_alertas']}")

            # Detalhar clientes desativados
            if data['clientes_desativados']:
                logging.warning("⚠️  CLIENTES DESATIVADOS:")
                for cliente in data['clientes_desativados']:
                    logging.warning(f"   - {cliente['cliente_nome']} (ID: {cliente['cliente_id']}) - Vencido em {cliente['data_validade']}")

            # Detalhar alertas
            if data['pedidos_a_vencer']:
                logging.info("📅 ALERTAS DE VENCIMENTO (próximos 10 dias):")
                for alerta in data['pedidos_a_vencer']:
                    logging.info(f"   - {alerta['cliente_nome']} ({alerta['plano_nome']}) - {alerta['dias_restantes']} dias restantes")
        else:
            logging.error(f"❌ Erro na API: Status {response.status_code}")
            logging.error(f"   Resposta: {response.text}")

    except requests.exceptions.ConnectionError:
        logging.error("❌ Erro: Não foi possível conectar ao backend. Certifique-se que está rodando.")
    except requests.exceptions.Timeout:
        logging.error("❌ Erro: Timeout ao conectar com o backend.")
    except Exception as e:
        logging.error(f"❌ Erro inesperado: {e}")

    logging.info("=" * 60)


def main():
    """Função principal"""
    logging.info("🚀 VERIFICADOR AUTOMÁTICO DE VENCIMENTOS INICIADO")
    logging.info(f"   API: {API_URL}")
    logging.info(f"   Horário de execução: Todo dia às 02:00")
    logging.info(f"   Log: /tmp/kairix-verificador.log")
    logging.info("=" * 60)

    # Executar imediatamente ao iniciar (para teste)
    logging.info("Executando verificação inicial...")
    verificar_vencimentos()

    # Agendar para executar todo dia às 2h da manhã
    schedule.every().day.at("02:00").do(verificar_vencimentos)

    logging.info("✅ Agendamento configurado com sucesso!")
    logging.info("   Aguardando próxima execução...")
    logging.info("")

    # Loop infinito verificando agendamentos
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica a cada 1 minuto


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\n👋 Verificador finalizado pelo usuário.")
    except Exception as e:
        logging.error(f"❌ Erro fatal: {e}")
