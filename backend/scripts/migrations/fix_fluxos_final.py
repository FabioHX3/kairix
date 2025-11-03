#!/usr/bin/env python3
"""
Script para adicionar preview na seção Fluxos de Conversa (texto correto)
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n' + '='*70)
print('📱 ADICIONANDO PREVIEW NA SEÇÃO FLUXOS (FINAL)')
print('='*70 + '\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ============================================================================
# MODIFICAR SEÇÃO FLUXOS DE CONVERSA - Texto correto
# ============================================================================

OLD_FLUXOS_SECTION = '''        <!-- Seção de Fluxos de Conversa -->
        <div class="content-section" id="section-fluxos">
            <div class="content-header">
                <h1>🔄 Fluxos de Conversa</h1>
                <p>Configure fluxos de conversa para diferentes situações</p>
            </div>

            <div class="section-card">'''

NEW_FLUXOS_SECTION = '''        <!-- Seção de Fluxos de Conversa -->
        <div class="content-section" id="section-fluxos">
            <div class="content-header">
                <h1>🔄 Fluxos de Conversa</h1>
                <p>Configure fluxos de conversa para diferentes situações</p>
            </div>

            <div class="preview-grid">
                <!-- Coluna de Configuração -->
                <div class="config-column">
            <div class="section-card">'''

if OLD_FLUXOS_SECTION in conteudo:
    conteudo = conteudo.replace(OLD_FLUXOS_SECTION, NEW_FLUXOS_SECTION)
    print('✅ Início da seção Fluxos modificada (grid)\n')
else:
    print('⚠️  Padrão OLD_FLUXOS_SECTION não encontrado (pode já estar modificado)\n')

# Adicionar preview no final da seção Fluxos
if 'preview-chat-fluxos' in conteudo:
    print('ℹ️  Preview já existe na seção Fluxos\n')
else:
    # Buscar o padrão que vem antes da seção de Upload
    OLD_FLUXOS_END = '''            </div>
        </div>

        <!-- Seção de Upload de Documentos -->'''

    NEW_FLUXOS_END = '''            </div>
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
        print('✅ Preview adicionado no final da seção Fluxos\n')
    else:
        print('⚠️  Padrão OLD_FLUXOS_END não encontrado\n')

# Salvar o arquivo
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('='*70)
print('✅ SEÇÃO FLUXOS ATUALIZADA!')
print('='*70 + '\n')
