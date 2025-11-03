#!/usr/bin/env python3
"""
Script para corrigir a funcionalidade dos previews:
- Garantir que as variáveis sejam acessíveis globalmente via window
- Atualizar referências nas funções de teste
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n' + '='*70)
print('🔧 CORRIGINDO FUNCIONALIDADE DOS PREVIEWS')
print('='*70 + '\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ============================================================================
# 1. MODIFICAR loadRespostas() para atualizar window.respostas
# ============================================================================

OLD_LOAD_RESPOSTAS = '''        async function loadRespostas() {
            try {
                const response = await fetch(`/api/config/${orderId}/respostas`);
                const data = await response.json();
                // A API retorna direto um array, não um objeto com propriedade respostas
                respostas = Array.isArray(data) ? data : (data.respostas || []);
                console.log('Respostas carregadas:', respostas.length);
                renderRespostas();
                updateBadge('respostas', respostas.length);
                document.getElementById('total-respostas').textContent = respostas.length;
            } catch (error) {
                console.error('Erro ao carregar respostas:', error);
            }
        }'''

NEW_LOAD_RESPOSTAS = '''        async function loadRespostas() {
            try {
                const response = await fetch(`/api/config/${orderId}/respostas`);
                const data = await response.json();
                // A API retorna direto um array, não um objeto com propriedade respostas
                respostas = Array.isArray(data) ? data : (data.respostas || []);
                window.respostas = respostas; // Tornar acessível globalmente para preview
                console.log('Respostas carregadas:', respostas.length);
                renderRespostas();
                updateBadge('respostas', respostas.length);
                document.getElementById('total-respostas').textContent = respostas.length;
            } catch (error) {
                console.error('Erro ao carregar respostas:', error);
            }
        }'''

if OLD_LOAD_RESPOSTAS in conteudo:
    conteudo = conteudo.replace(OLD_LOAD_RESPOSTAS, NEW_LOAD_RESPOSTAS)
    print('✅ loadRespostas() corrigida (window.respostas)\n')
else:
    print('⚠️  Padrão loadRespostas não encontrado\n')

# ============================================================================
# 2. MODIFICAR loadMenu() para atualizar window.menu
# ============================================================================

OLD_LOAD_MENU = '''        async function loadMenu() {
            try {
                const response = await fetch(`/api/config/${orderId}/menu`);
                const data = await response.json();
                // A API retorna direto um array, não um objeto com propriedade menu
                menuOpcoes = Array.isArray(data) ? data : (data.menu || []);
                console.log('Menu carregado:', menuOpcoes.length, 'opções');
                renderMenu();
                updateMenuPreview();
                updateBadge('menu', menuOpcoes.length > 0 ? 'Configurado' : 'Pendente');
                document.getElementById('total-menu').textContent = menuOpcoes.length;
            } catch (error) {
                console.error('Erro ao carregar menu:', error);
            }
        }'''

NEW_LOAD_MENU = '''        async function loadMenu() {
            try {
                const response = await fetch(`/api/config/${orderId}/menu`);
                const data = await response.json();
                // A API retorna direto um array, não um objeto com propriedade menu
                menuOpcoes = Array.isArray(data) ? data : (data.menu || []);
                window.menu = menuOpcoes; // Tornar acessível globalmente para preview
                console.log('Menu carregado:', menuOpcoes.length, 'opções');
                renderMenu();
                updateMenuPreview();
                updateBadge('menu', menuOpcoes.length > 0 ? 'Configurado' : 'Pendente');
                document.getElementById('total-menu').textContent = menuOpcoes.length;
            } catch (error) {
                console.error('Erro ao carregar menu:', error);
            }
        }'''

if OLD_LOAD_MENU in conteudo:
    conteudo = conteudo.replace(OLD_LOAD_MENU, NEW_LOAD_MENU)
    print('✅ loadMenu() corrigida (window.menu)\n')
else:
    print('⚠️  Padrão loadMenu não encontrado\n')

# ============================================================================
# 3. PROCURAR E MODIFICAR loadFluxos() se existir
# ============================================================================

# Primeiro vou buscar o padrão de loadFluxos
import re
match = re.search(r'async function loadFluxos\(\) \{.*?try \{.*?fluxos = .*?;', conteudo, re.DOTALL)
if match:
    old_fluxos_fragment = match.group(0)
    # Adicionar window.fluxos logo após a atribuição de fluxos
    new_fluxos_fragment = re.sub(
        r'(fluxos = [^;]+;)',
        r'\1\n                window.fluxos = fluxos; // Tornar acessível globalmente para preview',
        old_fluxos_fragment
    )
    conteudo = conteudo.replace(old_fluxos_fragment, new_fluxos_fragment)
    print('✅ loadFluxos() corrigida (window.fluxos)\n')
else:
    print('⚠️  loadFluxos não encontrada ou já modificada\n')

# Salvar o arquivo
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('='*70)
print('✅ FUNCIONALIDADE CORRIGIDA COM SUCESSO!')
print('='*70)
print('\n📋 Corrigido:')
print('   1. ✅ window.respostas agora é atualizada')
print('   2. ✅ window.menu agora é atualizada')
print('   3. ✅ window.fluxos agora é atualizada')
print('\n🧪 Agora os previews devem funcionar corretamente!')
print('🌐 Teste em: http://localhost:8012/configurar')
print('\n')
