#!/usr/bin/env python3
"""
Script para adicionar funcionalidade de submenu no Menu Interativo
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n' + '='*70)
print('📋 ADICIONANDO FUNCIONALIDADE DE SUBMENU')
print('='*70 + '\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ============================================================================
# 1. SUBSTITUIR FORMULÁRIO DE MENU
# ============================================================================

OLD_FORM = '''                <!-- Formulário de Nova/Editar Opção -->
                <div id="menu-form" style="display: none; margin-bottom: 30px; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 10px;">
                    <h4 id="menu-form-title">Nova Opção de Menu</h4>
                    <form id="form-menu" onsubmit="saveMenu(event)">
                        <input type="hidden" id="menu-id">
                        <div class="form-group">
                            <label>Número da Opção *</label>
                            <input type="text" id="menu-numero" placeholder="Ex: 1" required maxlength="1">
                            <small>Número de 1 a 9 que o cliente digitará para escolher esta opção</small>
                        </div>
                        <div class="form-group">
                            <label>Título da Opção *</label>
                            <input type="text" id="menu-titulo" placeholder="Ex: Falar com Atendente" required>
                            <small>O texto que aparecerá no menu</small>
                        </div>
                        <div class="form-group">
                            <label>Descrição (opcional)</label>
                            <textarea id="menu-descricao" placeholder="Ex: Será transferido para um atendente humano"></textarea>
                            <small>Explicação adicional sobre esta opção</small>
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button type="submit" class="btn btn-success">💾 Salvar</button>
                            <button type="button" class="btn btn-secondary" onclick="hideMenuForm()">❌ Cancelar</button>
                        </div>
                    </form>
                </div>'''

NEW_FORM = '''                <!-- Formulário de Nova/Editar Opção -->
                <div id="menu-form" style="display: none; margin-bottom: 30px; padding: 20px; background: rgba(255, 255, 255, 0.03); border-radius: 10px;">
                    <h4 id="menu-form-title">Nova Opção de Menu</h4>
                    <form id="form-menu" onsubmit="saveMenu(event)">
                        <input type="hidden" id="menu-id">
                        <div class="form-group">
                            <label>Número da Opção *</label>
                            <input type="text" id="menu-numero" placeholder="Ex: 1" required maxlength="1">
                            <small>Número de 1 a 9 que o cliente digitará para escolher esta opção</small>
                        </div>
                        <div class="form-group">
                            <label>Título da Opção *</label>
                            <input type="text" id="menu-titulo" placeholder="Ex: Falar com Atendente" required>
                            <small>O texto que aparecerá no menu</small>
                        </div>
                        <div class="form-group">
                            <label>Descrição (opcional)</label>
                            <textarea id="menu-descricao" placeholder="Ex: Será transferido para um atendente humano"></textarea>
                            <small>Explicação adicional sobre esta opção</small>
                        </div>

                        <div class="form-group">
                            <label>Tipo de Ação *</label>
                            <select id="menu-tipo-acao" onchange="toggleMenuActionFields()" required>
                                <option value="">Selecione...</option>
                                <option value="resposta">💬 Dar uma Resposta</option>
                                <option value="submenu">📋 Abrir Submenu</option>
                                <option value="atendente">👤 Transferir para Atendente</option>
                            </select>
                            <small>O que acontece quando o cliente escolhe esta opção</small>
                        </div>

                        <!-- Campo de Resposta (para tipo = resposta) -->
                        <div class="form-group" id="campo-resposta" style="display: none;">
                            <label>Resposta *</label>
                            <textarea id="menu-resposta" placeholder="Digite a mensagem que será enviada..."></textarea>
                            <small>Mensagem que o bot enviará quando esta opção for escolhida</small>
                        </div>

                        <!-- Campo de Submenu (para tipo = submenu) -->
                        <div id="campo-submenu" style="display: none;">
                            <div class="form-group">
                                <label>Sub-opções do Menu</label>
                                <div id="submenu-items" style="margin-bottom: 10px;"></div>
                                <button type="button" class="btn btn-sm btn-secondary" onclick="addSubmenuItem()">➕ Adicionar Sub-opção</button>
                                <small>Adicione as opções que aparecerão neste submenu</small>
                            </div>
                        </div>

                        <!-- Mensagem para Atendente (para tipo = atendente) -->
                        <div class="form-group" id="campo-atendente" style="display: none;">
                            <p style="background: rgba(37, 211, 102, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #25D366;">
                                ✅ <strong>Transferência para Atendente</strong><br>
                                <small>O cliente será informado que será transferido para um atendente humano.</small>
                            </p>
                        </div>

                        <div style="display: flex; gap: 10px; margin-top: 20px;">
                            <button type="submit" class="btn btn-success">💾 Salvar</button>
                            <button type="button" class="btn btn-secondary" onclick="hideMenuForm()">❌ Cancelar</button>
                        </div>
                    </form>
                </div>'''

if OLD_FORM in conteudo:
    conteudo = conteudo.replace(OLD_FORM, NEW_FORM)
    print('✅ Formulário de menu atualizado\n')
else:
    print('⚠️  Formulário não encontrado\n')

# Salvar
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('='*70)
print('✅ FORMULÁRIO ATUALIZADO COM SUCESSO!')
print('='*70)
print('\n📋 Próximo passo: Adicionar funções JavaScript')
print('\n')
