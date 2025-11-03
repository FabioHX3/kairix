#!/usr/bin/env python3
"""
Script para corrigir o CSS do submenu mobile nas páginas dos produtos
Adiciona display: block para que os links fiquem verticais
"""

OLD_CSS = """        .mobile-sidebar nav ul li .submenu a {
            padding: 10px 0;
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.8);
            border-left: 2px solid rgba(255, 90, 90, 0.3);
            padding-left: 15px;
            margin-bottom: 8px;
        }"""

NEW_CSS = """        .mobile-sidebar nav ul li .submenu a {
            display: block;
            padding: 10px 0;
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.8);
            border-left: 2px solid rgba(255, 90, 90, 0.3);
            padding-left: 15px;
            margin-bottom: 8px;
            text-decoration: none;
        }"""

arquivos = [
    '/mnt/c/PROJETOS/kairix/bot-normal.html',
    '/mnt/c/PROJETOS/kairix/bot-ia.html',
    '/mnt/c/PROJETOS/kairix/agente-financeiro.html'
]

for arquivo in arquivos:
    print(f'\n📄 Processando {arquivo}...')

    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if OLD_CSS in conteudo:
        conteudo = conteudo.replace(OLD_CSS, NEW_CSS)
        print('  ✅ CSS do submenu corrigido')

        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f'  ✅ {arquivo} atualizado!')
    else:
        print('  ⏭️  CSS já está correto ou formato diferente')

print('\n\n✅ Correção do CSS concluída!')
print('\nAgora os links do submenu aparecerão verticalmente (um embaixo do outro)')
print('ao invés de horizontalmente (em linha).')
