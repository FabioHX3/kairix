#!/usr/bin/env python3
"""
Script para corrigir o HTML do submenu nas páginas dos produtos
"""

OLD_HTML = '''                <li><a href="/#hero" onclick="closeMobileMenu()">Home</a></li>
                <li><a href="/#products" onclick="closeMobileMenu()">Soluções</a></li>
                <li><a href="/#benefits" onclick="closeMobileMenu()">Benefícios</a></li>'''

NEW_HTML = '''                <li><a href="/#hero" onclick="closeMobileMenu()">Home</a></li>
                <li class="has-submenu">
                    <a onclick="toggleSubmenu(event)">Soluções</a>
                    <div class="submenu">
                        <a href="http://localhost:8012/bot-normal.html" onclick="closeMobileMenu()">Bot Normal</a>
                        <a href="http://localhost:8012/bot-ia.html" onclick="closeMobileMenu()">Bot IA</a>
                        <a href="http://localhost:8012/agente-financeiro.html" onclick="closeMobileMenu()">Agente Financeiro</a>
                    </div>
                </li>
                <li><a href="/#benefits" onclick="closeMobileMenu()">Benefícios</a></li>'''

arquivos = [
    '/mnt/c/PROJETOS/kairix/bot-normal.html',
    '/mnt/c/PROJETOS/kairix/bot-ia.html',
    '/mnt/c/PROJETOS/kairix/agente-financeiro.html'
]

for arquivo in arquivos:
    print(f'\n📄 Processando {arquivo}...')

    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    if OLD_HTML in conteudo:
        conteudo = conteudo.replace(OLD_HTML, NEW_HTML)
        print('  ✅ HTML do submenu substituído')

        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f'  ✅ {arquivo} atualizado!')
    else:
        print('  ⏭️  HTML já atualizado ou formato diferente')

print('\n\n✅ Correção do HTML concluída!')
