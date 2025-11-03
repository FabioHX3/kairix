#!/usr/bin/env python3
"""
Script para ocultar o floating-phone em dispositivos mobile
"""

OLD_CSS = """            .phone {
                position: relative;
                top: auto;
                left: auto;
                transform: rotateY(0deg) rotateX(0deg) scale(0.8);
                margin: 0 auto;
            }

            .phone:hover {
                transform: rotateY(0deg) rotateX(0deg) scale(0.85);
            }"""

NEW_CSS = """            /* Ocultar floating-phone em mobile */
            .phone {
                display: none !important;
            }"""

arquivos = [
    '/mnt/c/PROJETOS/kairix/index.html',
    '/mnt/c/PROJETOS/kairix/bot-normal.html',
    '/mnt/c/PROJETOS/kairix/bot-ia.html',
    '/mnt/c/PROJETOS/kairix/agente-financeiro.html'
]

print('\n═══════════════════════════════════════════════════════')
print('📱 OCULTANDO FLOATING-PHONE EM RESOLUÇÃO MOBILE')
print('═══════════════════════════════════════════════════════\n')

for arquivo in arquivos:
    nome_arquivo = arquivo.split('/')[-1]
    print(f'📄 {nome_arquivo}...')

    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()

        if OLD_CSS in conteudo:
            conteudo = conteudo.replace(OLD_CSS, NEW_CSS)

            with open(arquivo, 'w', encoding='utf-8') as f:
                f.write(conteudo)
            print(f'   ✅ Floating-phone oculto em mobile!\n')
        else:
            print(f'   ⏭️  Não encontrado ou já modificado\n')
    except FileNotFoundError:
        print(f'   ⚠️  Arquivo não encontrado\n')

print('═══════════════════════════════════════════════════════')
print('✅ CORREÇÃO CONCLUÍDA!')
print('═══════════════════════════════════════════════════════')
print('\n📱 O celular flutuante agora estará OCULTO em:')
print('   • Smartphones (largura < 768px)')
print('   • Tablets em modo portrait')
print('   • Navegador redimensionado para mobile')
print('\n💻 E continuará VISÍVEL em:')
print('   • Desktop')
print('   • Tablets em modo landscape')
print('   • Telas maiores que 768px')
print('\n═══════════════════════════════════════════════════════\n')
