#!/usr/bin/env python3
"""
Script para limpar opções de menu antigas que não têm o campo 'acao'
"""
from database import SessionLocal
from models import OpcoesMenu

def limpar_menu_antigo():
    """Remove opções de menu antigas sem o campo 'acao'"""

    db = SessionLocal()

    try:
        # Buscar todas as opções
        opcoes = db.query(OpcoesMenu).all()

        if not opcoes:
            print("✅ Nenhuma opção de menu antiga encontrada")
            return True

        print(f"📋 Encontradas {len(opcoes)} opções de menu antigas")

        # Deletar todas
        for opcao in opcoes:
            print(f"   🗑️  Removendo: {opcao.numero}. {opcao.titulo}")
            db.delete(opcao)

        db.commit()
        print(f"✅ {len(opcoes)} opções antigas removidas com sucesso!")

        return True

    except Exception as e:
        print(f"❌ Erro ao limpar menu: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("🧹 LIMPANDO MENU ANTIGO")
    print("="*60)
    success = limpar_menu_antigo()
    if success:
        print("\n✅ PRONTO! Menu antigo removido")
    else:
        print("\n❌ Falhou ao limpar menu")
    print("="*60)
