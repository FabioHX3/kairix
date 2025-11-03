"""
Script para popular dados de métricas de exemplo
"""
from database import SessionLocal
import models
from datetime import date, timedelta
import random

db = SessionLocal()

# Buscar o cliente existente
cliente = db.query(models.Cliente).first()

if not cliente:
    print("❌ Nenhum cliente encontrado. Execute o sistema primeiro.")
    db.close()
    exit(1)

print(f"📊 Populando métricas para cliente: {cliente.nome}")

# Limpar métricas existentes (se houver)
db.query(models.MetricaDiaria).filter(models.MetricaDiaria.cliente_id == cliente.id).delete()
db.commit()

# Criar métricas para os últimos 7 dias
hoje = date.today()
metricas_criadas = 0

for dias_atras in range(6, -1, -1):
    data_metrica = hoje - timedelta(days=dias_atras)

    # Dados crescentes ao longo da semana (simulando crescimento)
    fator_crescimento = 1 + (0.15 * (6 - dias_atras))

    metrica = models.MetricaDiaria(
        cliente_id=cliente.id,
        data=data_metrica,
        total_mensagens=int(random.randint(45, 75) * fator_crescimento),
        total_contatos=int(random.randint(12, 22) * fator_crescimento),
        conversas_iniciadas=int(random.randint(8, 15) * fator_crescimento),
        conversas_finalizadas=int(random.randint(6, 12) * fator_crescimento),
        tempo_resposta_medio=random.uniform(0.5, 1.2),
        taxa_conversao=random.uniform(55.0, 85.0)
    )

    db.add(metrica)
    metricas_criadas += 1
    print(f"  ✅ {data_metrica.strftime('%d/%m')} - {metrica.total_mensagens} mensagens, {metrica.total_contatos} contatos")

db.commit()
db.close()

print(f"\n✅ {metricas_criadas} métricas criadas com sucesso!")
print("🎉 Agora o gráfico terá dados reais para exibir!")
