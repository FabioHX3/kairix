"""
Script para adicionar campo de senha na tabela de clientes
"""
from sqlalchemy import text
from database import engine
import hashlib

def hash_password(password: str) -> str:
    """Gera hash da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def add_password_field():
    """Adiciona coluna senha_hash na tabela clientes"""

    print("🔐 Adicionando campo de senha na tabela clientes...")

    with engine.connect() as connection:
        try:
            # Adicionar coluna senha_hash
            connection.execute(text('''
                ALTER TABLE clientes
                ADD COLUMN IF NOT EXISTS senha_hash VARCHAR(200)
            '''))
            connection.commit()
            print("✅ Coluna senha_hash adicionada")

            # Atualizar clientes existentes com senha padrão
            # Senha padrão será o número do WhatsApp (sem formatação)
            connection.execute(text('''
                UPDATE clientes
                SET senha_hash = NULL
                WHERE senha_hash IS NULL
            '''))

            # Para cada cliente, gerar hash do WhatsApp como senha temporária
            result = connection.execute(text('SELECT id, whatsapp FROM clientes'))
            clientes = result.fetchall()

            for cliente_id, whatsapp in clientes:
                # Remover formatação do WhatsApp
                senha_temp = ''.join(filter(str.isdigit, whatsapp))
                senha_hash = hash_password(senha_temp)

                connection.execute(
                    text('UPDATE clientes SET senha_hash = :senha WHERE id = :id'),
                    {'senha': senha_hash, 'id': cliente_id}
                )
                print(f"  Cliente #{cliente_id}: Senha temporária definida (use seu WhatsApp: {senha_temp})")

            connection.commit()

            # Tornar coluna NOT NULL
            connection.execute(text('''
                ALTER TABLE clientes
                ALTER COLUMN senha_hash SET NOT NULL
            '''))
            connection.commit()
            print("✅ Campo senha_hash configurado como obrigatório")

        except Exception as e:
            print(f"❌ Erro: {e}")
            connection.rollback()
            raise

    print("\n✅ Migração concluída!")
    print("\n📝 IMPORTANTE:")
    print("   Todos os clientes existentes podem fazer login usando:")
    print("   - Email: (email cadastrado)")
    print("   - Senha: (número do WhatsApp sem formatação)")
    print("   Exemplo: Se o WhatsApp é (65) 99934-2690, a senha é: 65999342690")

if __name__ == "__main__":
    add_password_field()
