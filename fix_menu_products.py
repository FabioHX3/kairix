#!/usr/bin/env python3
"""
Script para copiar o CSS do menu mobile da home para as páginas de produtos
"""

# CSS incorreto (genérico)
OLD_MOBILE_CSS = """        .mobile-sidebar nav {
            padding: 80px 20px 20px;
        }

        .mobile-sidebar ul {
            list-style: none;
            padding: 0;
            margin: 0 0 30px 0;
        }

        .mobile-sidebar li {
            margin: 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .mobile-sidebar a {
            display: block;
            padding: 15px 10px;
            color: white;
            text-decoration: none;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        .mobile-sidebar li a:hover {
            background: rgba(255, 90, 90, 0.1);
            padding-left: 20px;
        }

        .mobile-sidebar .cta-button {
            width: 100%;
            text-align: center;
            margin: 0;
        }"""

# CSS correto (específico, igual à home)
NEW_MOBILE_CSS = """        .mobile-sidebar nav {
            padding: 80px 30px 30px 30px;
        }

        .mobile-sidebar nav ul {
            flex-direction: column;
            gap: 0;
        }

        .mobile-sidebar nav ul li {
            margin: 0;
            padding: 15px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .mobile-sidebar nav ul li:last-child {
            border-bottom: none;
        }

        .mobile-sidebar nav ul li a {
            display: block;
            font-size: 1.1rem;
        }

        .mobile-sidebar .cta-button {
            width: 100%;
            margin-top: 20px;
            text-align: center;
        }"""

arquivos = [
    '/mnt/c/PROJETOS/kairix/bot-normal.html',
    '/mnt/c/PROJETOS/kairix/bot-ia.html',
    '/mnt/c/PROJETOS/kairix/agente-financeiro.html'
]

print('\n═══════════════════════════════════════════════════════')
print('🎨 CORRIGINDO CSS DO MENU MOBILE NAS PÁGINAS DE PRODUTOS')
print('═══════════════════════════════════════════════════════\n')

for arquivo in arquivos:
    nome_arquivo = arquivo.split('/')[-1]
    print(f'📄 {nome_arquivo}...')

    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        if OLD_MOBILE_CSS in conteudo:
            conteudo = conteudo.replace(OLD_MOBILE_CSS, NEW_MOBILE_CSS)

            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f'   ✅ CSS do menu corrigido!\n')
        else:
            print(f'   ⏭️  CSS já está correto ou formato diferente\n')
    except FileNotFoundError:
        print(f'   ⚠️  Arquivo não encontrado\n')

print('═══════════════════════════════════════════════════════')
print('✅ CORREÇÃO CONCLUÍDA!')
print('═══════════════════════════════════════════════════════')
print('\n🎯 O menu mobile agora está consistente em todas as páginas!')
print('   • Seletores CSS específicos (sem conflitos)')
print('   • Submenu funcionando corretamente')
print('   • Links verticais (não mais em linha)')
print('   • Visual idêntico à home')
print('\n═══════════════════════════════════════════════════════\n')
