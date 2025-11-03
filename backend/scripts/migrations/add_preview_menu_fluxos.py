#!/usr/bin/env python3
"""
Script para adicionar preview do celular WhatsApp nas seções:
- Menu Interativo
- Fluxos de Conversa
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n' + '='*70)
print('📱 ADICIONANDO PREVIEW NAS SEÇÕES MENU E FLUXOS')
print('='*70 + '\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ============================================================================
# 1. MODIFICAR SEÇÃO MENU INTERATIVO
# ============================================================================

OLD_MENU_SECTION = '''        <!-- Seção de Menu Interativo -->
        <div class="content-section" id="section-menu">
            <div class="content-header">
                <h1>📋 Menu Interativo</h1>
                <p>Crie menus de opções para o usuário escolher</p>
            </div>

            <div class="section-card">'''

NEW_MENU_SECTION = '''        <!-- Seção de Menu Interativo -->
        <div class="content-section" id="section-menu">
            <div class="content-header">
                <h1>📋 Menu Interativo</h1>
                <p>Crie menus de opções para o usuário escolher</p>
            </div>

            <div class="preview-grid">
                <!-- Coluna de Configuração -->
                <div class="config-column">
            <div class="section-card">'''

if OLD_MENU_SECTION in conteudo:
    conteudo = conteudo.replace(OLD_MENU_SECTION, NEW_MENU_SECTION)
    print('✅ Início da seção Menu modificada (grid)\n')
else:
    print('⏭️  Seção Menu já tem grid ou não encontrada\n')

# Adicionar preview ao final da seção Menu (antes do </div> final)
OLD_MENU_END = '''                </div>
            </div>
        </div>

        <!-- Seção de Fluxos de Conversa -->'''

NEW_MENU_END = '''                </div>
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
                            <div class="preview-chat" id="preview-chat-menu">
                                <div class="preview-msg preview-msg-bot">Olá! Bem-vindo ao nosso atendimento.</div>
                                <div class="preview-msg preview-msg-bot" id="menu-preview-options">
                                    <div style="font-weight: 600; margin-bottom: 10px;">Escolha uma opção:</div>
                                </div>
                            </div>
                            <div class="preview-input-box">
                                <input type="text" id="preview-input-menu" placeholder="Digite para testar..." onkeypress="if(event.key==='Enter') testPreviewMenu()">
                                <button onclick="testPreviewMenu()">▶</button>
                            </div>
                        </div>
                    </div>
                    <p class="preview-helper-text">💡 Clique nas opções do menu</p>
                </div>
            </div>
        </div>

        <!-- Seção de Fluxos de Conversa -->'''

if OLD_MENU_END in conteudo:
    conteudo = conteudo.replace(OLD_MENU_END, NEW_MENU_END)
    print('✅ Preview adicionado na seção Menu\n')
else:
    print('⏭️  Preview já existe ou não encontrado\n')

# ============================================================================
# 2. MODIFICAR SEÇÃO FLUXOS DE CONVERSA
# ============================================================================

OLD_FLUXOS_SECTION = '''        <!-- Seção de Fluxos de Conversa -->
        <div class="content-section" id="section-fluxos">
            <div class="content-header">
                <h1>🔄 Fluxos de Conversa</h1>
                <p>Configure fluxos completos de atendimento</p>
            </div>

            <div class="section-card">'''

NEW_FLUXOS_SECTION = '''        <!-- Seção de Fluxos de Conversa -->
        <div class="content-section" id="section-fluxos">
            <div class="content-header">
                <h1>🔄 Fluxos de Conversa</h1>
                <p>Configure fluxos completos de atendimento</p>
            </div>

            <div class="preview-grid">
                <!-- Coluna de Configuração -->
                <div class="config-column">
            <div class="section-card">'''

if OLD_FLUXOS_SECTION in conteudo:
    conteudo = conteudo.replace(OLD_FLUXOS_SECTION, NEW_FLUXOS_SECTION)
    print('✅ Início da seção Fluxos modificada (grid)\n')
else:
    print('⏭️  Seção Fluxos já tem grid ou não encontrada\n')

# Adicionar preview ao final da seção Fluxos
# Buscar o fechamento da seção (antes da seção de Upload de Documentos)
OLD_FLUXOS_END = '''                </div>
            </div>
        </div>

        <!-- Seção de Upload de Documentos -->'''

NEW_FLUXOS_END = '''                </div>
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
                            <div class="preview-chat" id="preview-chat-fluxos">
                                <div class="preview-msg preview-msg-bot">Olá! Bem-vindo ao nosso atendimento.</div>
                            </div>
                            <div class="preview-input-box">
                                <input type="text" id="preview-input-fluxos" placeholder="Digite para testar..." onkeypress="if(event.key==='Enter') testPreviewFluxos()">
                                <button onclick="testPreviewFluxos()">▶</button>
                            </div>
                        </div>
                    </div>
                    <p class="preview-helper-text">💡 Teste os fluxos de conversa</p>
                </div>
            </div>
        </div>

        <!-- Seção de Upload de Documentos -->'''

if OLD_FLUXOS_END in conteudo:
    conteudo = conteudo.replace(OLD_FLUXOS_END, NEW_FLUXOS_END)
    print('✅ Preview adicionado na seção Fluxos\n')
else:
    print('⏭️  Preview já existe ou não encontrado\n')

# Salvar o arquivo
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('='*70)
print('✅ PREVIEW ADICIONADO COM SUCESSO EM MENU E FLUXOS!')
print('='*70)
print('\n📋 Próximo passo:')
print('   → Criar funções JavaScript de teste para os previews')
print('\n')
