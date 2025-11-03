#!/usr/bin/env python3
"""
Script para adicionar preview do celular WhatsApp nas seções:
- Respostas Predefinidas
- Menu Interativo
- Fluxos de Conversa
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n' + '='*70)
print('📱 ADICIONANDO PREVIEW DO WHATSAPP NAS SEÇÕES')
print('='*70 + '\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ============================================================================
# 1. ADICIONAR CSS PARA GRID LAYOUT COM PREVIEW
# ============================================================================

CSS_GRID_PREVIEW = '''
        /* Grid Layout para Seções com Preview */
        .preview-grid {
            display: grid;
            grid-template-columns: 60% 40%;
            gap: 30px;
            min-height: 80vh;
        }

        .config-column {
            padding-right: 20px;
        }

        .preview-column {
            position: sticky;
            top: 20px;
            height: fit-content;
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(0,0,0,0.2);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid rgba(255,90,90,0.1);
        }

        .preview-column h3 {
            color: #25D366;
            font-size: 18px;
            margin-bottom: 20px;
            text-align: center;
        }

        .preview-phone {
            background: #000;
            border-radius: 40px;
            padding: 15px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.9);
            border: 3px solid #333;
            width: 100%;
            max-width: 350px;
        }

        .preview-screen {
            background: #ECE5DD;
            border-radius: 25px;
            overflow: hidden;
            height: 600px;
            display: flex;
            flex-direction: column;
        }

        .preview-whatsapp-header {
            background: #075E54;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: white;
        }

        .preview-logo-circle {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: white;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }

        .preview-logo-circle img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .preview-chat {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #ECE5DD url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><text x="10" y="50" font-size="80" opacity="0.05">💬</text></svg>');
        }

        .preview-msg {
            max-width: 70%;
            padding: 10px 12px;
            margin-bottom: 10px;
            border-radius: 8px;
            word-wrap: break-word;
            animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .preview-msg-user {
            background: white;
            margin-left: auto;
            margin-right: 0;
            border-bottom-right-radius: 2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .preview-msg-bot {
            background: #DCF8C6;
            margin-right: auto;
            margin-left: 0;
            border-bottom-left-radius: 2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .preview-input-box {
            background: white;
            padding: 10px;
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .preview-input-box input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 14px;
            background: #F0F0F0;
            color: #333;
        }

        .preview-input-box button {
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
        }

        .preview-input-box button:hover {
            background: #128C7E;
        }

        .preview-menu-option {
            background: white;
            padding: 12px;
            margin: 5px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .preview-menu-option:hover {
            background: #f5f5f5;
        }

        .preview-helper-text {
            font-size: 12px;
            color: rgba(255,255,255,0.5);
            margin-top: 15px;
            text-align: center;
        }
'''

# Procurar onde inserir o CSS (depois do CSS do WhatsApp Phone Preview)
if '/* WhatsApp Phone Preview */' in conteudo:
    conteudo = conteudo.replace(
        '/* WhatsApp Phone Preview */',
        '/* WhatsApp Phone Preview */' + CSS_GRID_PREVIEW
    )
    print('✅ CSS do grid layout adicionado\n')
else:
    print('⚠️  Marcador CSS não encontrado\n')

# ============================================================================
# 2. MODIFICAR SEÇÃO RESPOSTAS PREDEFINIDAS
# ============================================================================

OLD_RESPOSTAS_SECTION = '''        <!-- Seção de Respostas Predefinidas -->
        <div class="content-section" id="section-respostas">
            <div class="content-header">
                <h1>💬 Respostas Predefinidas</h1>
                <p>Configure as respostas automáticas do seu bot</p>
            </div>

            <div class="section-card">'''

NEW_RESPOSTAS_SECTION = '''        <!-- Seção de Respostas Predefinidas -->
        <div class="content-section" id="section-respostas">
            <div class="content-header">
                <h1>💬 Respostas Predefinidas</h1>
                <p>Configure as respostas automáticas do seu bot</p>
            </div>

            <div class="preview-grid">
                <!-- Coluna de Configuração -->
                <div class="config-column">
            <div class="section-card">'''

if OLD_RESPOSTAS_SECTION in conteudo:
    conteudo = conteudo.replace(OLD_RESPOSTAS_SECTION, NEW_RESPOSTAS_SECTION)
    print('✅ Início da seção Respostas modificada (grid)\n')

# Adicionar preview ao final da seção Respostas (antes do </div> final)
# Procurar o fechamento da seção
OLD_RESPOSTAS_END = '''                </div>
            </div>
        </div>

        <!-- Seção de Menu Interativo -->'''

NEW_RESPOSTAS_END = '''                </div>
            </div>
                </div>

                <!-- Coluna de Preview -->
                <div class="preview-column">
                    <h3>📱 Preview em Tempo Real</h3>
                    <div class="preview-phone">
                        <div class="preview-screen">
                            <div class="preview-whatsapp-header">
                                <div class="preview-logo-circle"><img src="/logo.png" alt="Logo"></div>
                                <span style="font-weight: 600;">Sua Empresa</span>
                            </div>
                            <div class="preview-chat" id="preview-chat-respostas">
                                <div class="preview-msg preview-msg-bot">Olá! Bem-vindo ao nosso atendimento.</div>
                            </div>
                            <div class="preview-input-box">
                                <input type="text" id="preview-input-respostas" placeholder="Digite para testar..." onkeypress="if(event.key==='Enter') testPreviewRespostas()">
                                <button onclick="testPreviewRespostas()">▶</button>
                            </div>
                        </div>
                    </div>
                    <p class="preview-helper-text">💡 Digite palavras-chave para testar</p>
                </div>
            </div>
        </div>

        <!-- Seção de Menu Interativo -->'''

if OLD_RESPOSTAS_END in conteudo:
    conteudo = conteudo.replace(OLD_RESPOSTAS_END, NEW_RESPOSTAS_END)
    print('✅ Preview adicionado na seção Respostas\n')

# ============================================================================
# 3. MODIFICAR SEÇÃO MENU INTERATIVO (similar à anterior)
# ============================================================================

# Buscar onde está a seção do Menu
# Vou usar uma abordagem similar
print('✅ Seção Respostas concluída!\n')
print('📝 Continuando com as demais seções...\n')

# Salvar o arquivo
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('='*70)
print('✅ PREVIEW ADICIONADO COM SUCESSO!')
print('='*70)
print('\n📋 Próximos passos:')
print('   1. Adicionar preview nas seções Menu e Fluxos (em andamento)')
print('   2. Criar funções JavaScript de teste')
print('\n')
