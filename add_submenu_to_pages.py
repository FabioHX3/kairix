#!/usr/bin/env python3
"""
Script para adicionar submenu mobile nas páginas dos produtos
"""

CSS_SUBMENU = """
        /* Submenu Mobile */
        .mobile-sidebar nav ul li.has-submenu > a {
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }

        .mobile-sidebar nav ul li.has-submenu > a::after {
            content: '▼';
            font-size: 0.8rem;
            transition: transform 0.3s ease;
        }

        .mobile-sidebar nav ul li.has-submenu.open > a::after {
            transform: rotate(180deg);
        }

        .mobile-sidebar nav ul li .submenu {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            padding-left: 20px;
        }

        .mobile-sidebar nav ul li.has-submenu.open .submenu {
            max-height: 300px;
            margin-top: 10px;
        }

        .mobile-sidebar nav ul li .submenu a {
            padding: 10px 0;
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.8);
            border-left: 2px solid rgba(255, 90, 90, 0.3);
            padding-left: 15px;
            margin-bottom: 8px;
        }

        .mobile-sidebar nav ul li .submenu a:hover {
            color: #FF5A5A;
            border-left-color: #FF5A5A;
        }
    </style>"""

HTML_SUBMENU = """                <li class="has-submenu">
                    <a onclick="toggleSubmenu(event)">Soluções</a>
                    <div class="submenu">
                        <a href="http://localhost:8012/bot-normal.html" onclick="closeMobileMenu()">Bot Normal</a>
                        <a href="http://localhost:8012/bot-ia.html" onclick="closeMobileMenu()">Bot IA</a>
                        <a href="http://localhost:8012/agente-financeiro.html" onclick="closeMobileMenu()">Agente Financeiro</a>
                    </div>
                </li>"""

JS_FUNCTION = """
        function toggleSubmenu(event) {
            event.preventDefault();
            const parentLi = event.target.closest('li.has-submenu');
            parentLi.classList.toggle('open');
        }
    </script>"""

arquivos = [
    '/mnt/c/PROJETOS/kairix/bot-normal.html',
    '/mnt/c/PROJETOS/kairix/bot-ia.html',
    '/mnt/c/PROJETOS/kairix/agente-financeiro.html'
]

for arquivo in arquivos:
    print(f'\n📄 Processando {arquivo}...')

    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 1. Adicionar CSS do submenu antes do </style>
    if 'Submenu Mobile' not in conteudo:
        conteudo = conteudo.replace('    </style>', CSS_SUBMENU)
        print('  ✅ CSS do submenu adicionado')
    else:
        print('  ⏭️  CSS do submenu já existe')

    # 2. Substituir o link simples "Soluções" pelo submenu
    old_solucoes = '<li><a href="#products" onclick="closeMobileMenu()">Soluções</a></li>'
    if old_solucoes in conteudo:
        conteudo = conteudo.replace(old_solucoes, HTML_SUBMENU)
        print('  ✅ HTML do submenu adicionado')
    else:
        print('  ⏭️  HTML do submenu já existe ou formato diferente')

    # 3. Adicionar função JavaScript antes do </script>
    if 'function toggleSubmenu' not in conteudo:
        conteudo = conteudo.replace('    </script>', JS_FUNCTION)
        print('  ✅ Função JavaScript adicionada')
    else:
        print('  ⏭️  Função JavaScript já existe')

    # Salvar arquivo
    with open(arquivo, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print(f'  ✅ {arquivo} atualizado!')

print('\n\n✅ Todos os arquivos foram atualizados com sucesso!')
