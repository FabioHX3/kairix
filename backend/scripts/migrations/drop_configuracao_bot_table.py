#!/usr/bin/env python3
"""
Script para remover a tabela ConfiguracaoBot do banco de dados.
"""

from database import engine
from sqlalchemy import text

print('\n' + '='*60)
print('🗑️  REMOVENDO TABELA ConfiguracaoBot')
print('='*60 + '\n')

try:
    with engine.connect() as connection:
        # Verificar se a tabela existe
        result = connection.execute(text(
            "SELECT EXISTS ("
            "SELECT FROM information_schema.tables "
            "WHERE table_name = 'configuracoes_bot'"
            ")"
        ))
        table_exists = result.scalar()

        if not table_exists:
            print('ℹ️  Tabela "configuracoes_bot" não existe no banco de dados.')
            print('✅ Nada a fazer.\n')
        else:
            print('📋 Tabela "configuracoes_bot" encontrada.')
            print('🗑️  Removendo tabela...\n')

            # Dropar a tabela
            connection.execute(text('DROP TABLE IF EXISTS configuracoes_bot CASCADE'))
            connection.commit()

            print('✅ Tabela "configuracoes_bot" removida com sucesso!')
            print('✅ Todas as constraints e foreign keys foram removidas.\n')

except Exception as e:
    print(f'❌ Erro ao remover tabela: {e}\n')
    raise

print('='*60)
print('✅ OPERAÇÃO CONCLUÍDA')
print('='*60 + '\n')
