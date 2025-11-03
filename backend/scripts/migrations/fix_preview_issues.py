#!/usr/bin/env python3
"""
Script para corrigir os problemas do preview:
1. Texto branco (adicionar cor preta)
2. Botão oval (ajustar CSS)
3. Funcionalidade de respostas e menu
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n' + '='*70)
print('🔧 CORRIGINDO PROBLEMAS DO PREVIEW')
print('='*70 + '\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ============================================================================
# 1. CORRIGIR TEXTO BRANCO - Adicionar cor preta nas mensagens
# ============================================================================

OLD_PREVIEW_MSG = '''        .preview-msg {
            max-width: 70%;
            padding: 10px 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            word-wrap: break-word;
            animation: fadeIn 0.3s;
        }'''

NEW_PREVIEW_MSG = '''        .preview-msg {
            max-width: 70%;
            padding: 10px 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            word-wrap: break-word;
            animation: fadeIn 0.3s;
            color: #000;
            font-size: 14px;
        }'''

if OLD_PREVIEW_MSG in conteudo:
    conteudo = conteudo.replace(OLD_PREVIEW_MSG, NEW_PREVIEW_MSG)
    print('✅ Cor do texto corrigida (preto)\n')
else:
    print('⚠️  Padrão .preview-msg não encontrado\n')

# ============================================================================
# 2. CORRIGIR BOTÃO OVAL - Garantir botão perfeitamente circular
# ============================================================================

OLD_BUTTON = '''        .preview-input-box button {
            background: #25D366;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: pointer;
            font-size: 18px;
        }'''

NEW_BUTTON = '''        .preview-input-box button {
            background: #25D366;
            border: none;
            border-radius: 50%;
            width: 42px;
            height: 42px;
            min-width: 42px;
            min-height: 42px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: pointer;
            font-size: 18px;
            padding: 0;
            flex-shrink: 0;
        }'''

if OLD_BUTTON in conteudo:
    conteudo = conteudo.replace(OLD_BUTTON, NEW_BUTTON)
    print('✅ Botão corrigido (circular perfeito)\n')
else:
    print('⚠️  Padrão do botão não encontrado\n')

# ============================================================================
# 3. ADICIONAR COR NO TEXTO DAS OPÇÕES DE MENU
# ============================================================================

OLD_MENU_OPTION = '''        .preview-menu-option {
            background: white;
            padding: 12px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }'''

NEW_MENU_OPTION = '''        .preview-menu-option {
            background: white;
            padding: 12px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            color: #000;
            font-size: 14px;
        }'''

if OLD_MENU_OPTION in conteudo:
    conteudo = conteudo.replace(OLD_MENU_OPTION, NEW_MENU_OPTION)
    print('✅ Cor do texto do menu corrigida\n')
else:
    print('⚠️  Padrão .preview-menu-option não encontrado\n')

# Salvar o arquivo
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('='*70)
print('✅ CORREÇÕES APLICADAS COM SUCESSO!')
print('='*70)
print('\n📋 Corrigido:')
print('   1. ✅ Texto preto nas mensagens (legível)')
print('   2. ✅ Botão perfeitamente circular')
print('   3. ✅ Texto preto nas opções de menu')
print('\n🌐 Teste agora em: http://localhost:8012/configurar')
print('\n')
