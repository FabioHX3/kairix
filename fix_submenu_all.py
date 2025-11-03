#!/usr/bin/env python3
"""
Script para corrigir o CSS do submenu mobile em TODAS as páginas
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
    '/mnt/c/PROJETOS/kairix/index.html',
    '/mnt/c/PROJETOS/kairix/bot-normal.html',
    '/mnt/c/PROJETOS/kairix/bot-ia.html',
    '/mnt/c/PROJETOS/kairix/agente-financeiro.html'
]

print('\n═══════════════════════════════════════════════════════')
print('🔧 CORRIGINDO CSS DO SUBMENU MOBILE EM TODAS AS PÁGINAS')
print('═══════════════════════════════════════════════════════\n')

for arquivo in arquivos:
    nome_arquivo = arquivo.split('/')[-1]
    print(f'📄 {nome_arquivo}...')

    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if OLD_CSS in conteudo:
        conteudo = conteudo.replace(OLD_CSS, NEW_CSS)

        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f'   ✅ Corrigido! Links agora aparecem verticalmente\n')
    else:
        print(f'   ⏭️  Já está correto ou formato diferente\n')

print('═══════════════════════════════════════════════════════')
print('✅ CORREÇÃO CONCLUÍDA!')
print('═══════════════════════════════════════════════════════')
print('\n📱 Agora o submenu mobile está consistente em todas as páginas:')
print('   • index.html (home)')
print('   • bot-normal.html')
print('   • bot-ia.html')
print('   • agente-financeiro.html')
print('\n🎯 Os links do submenu aparecerão um embaixo do outro,')
print('   ao invés de em linha horizontal.')
print('\n═══════════════════════════════════════════════════════\n')
