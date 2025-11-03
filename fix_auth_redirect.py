#!/usr/bin/env python3
"""
Script para corrigir autenticação e redirecionamentos
"""

arquivo = '/mnt/c/PROJETOS/kairix/backend/static/configurar.html'

print('\n═══════════════════════════════════════════════════════')
print('🔐 CORRIGINDO AUTENTICAÇÃO E REDIRECIONAMENTOS')
print('═══════════════════════════════════════════════════════\n')

with open(arquivo, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# 1. Remover onclick do botão "Configuração do Agente"
OLD_BUTTON = '''            <div class="menu-item" onclick="goToConfigPanel()">
                <span class="menu-item-icon">🤖</span>
                <span class="menu-item-text">Configuração do Agente</span>
            </div>'''

NEW_BUTTON = '''            <div class="menu-item active">
                <span class="menu-item-icon">🤖</span>
                <span class="menu-item-text">Configuração do Agente</span>
            </div>'''

if OLD_BUTTON in conteudo:
    conteudo = conteudo.replace(OLD_BUTTON, NEW_BUTTON)
    print('✅ Botão "Configuração do Agente" corrigido')
    print('   - Removido redirecionamento')
    print('   - Agora apenas indica a página atual\n')
else:
    print('⏭️  Botão já está correto\n')

# 2. Substituir alert por redirecionamento para login
OLD_FUNCTION = '''        // Redirecionar para o painel de configuração completo
        function goToConfigPanel() {
            if (currentClientId) {
                window.location.href = `/painel/${currentClientId}`;
            } else {
                alert('Erro: Cliente não identificado. Recarregue a página.');
            }
        }'''

NEW_FUNCTION = '''        // Redirecionar para login se não tiver cliente
        function goToConfigPanel() {
            if (!currentClientId) {
                window.location.href = '/login';
            }
        }'''

if OLD_FUNCTION in conteudo:
    conteudo = conteudo.replace(OLD_FUNCTION, NEW_FUNCTION)
    print('✅ Função goToConfigPanel() corrigida')
    print('   - Removido alert chato')
    print('   - Redireciona para /login automaticamente\n')
else:
    print('⏭️  Função já está correta\n')

# 3. Adicionar verificação no início da função init()
OLD_INIT = '''        async function init() {
            document.getElementById('productName').textContent = getProductName(agentType);
            document.getElementById('planName').textContent = planName;

            // Buscar client_id do pedido'''

NEW_INIT = '''        async function init() {
            // Verificar se há orderId nos parâmetros da URL
            if (!orderId) {
                console.warn('Nenhum pedido especificado. Redirecionando para login.');
                window.location.href = '/login';
                return;
            }

            document.getElementById('productName').textContent = getProductName(agentType);
            document.getElementById('planName').textContent = planName;

            // Buscar client_id do pedido'''

if OLD_INIT in conteudo:
    conteudo = conteudo.replace(OLD_INIT, NEW_INIT)
    print('✅ Função init() corrigida')
    print('   - Verifica se tem orderId')
    print('   - Redireciona para /login se não tiver\n')
else:
    print('⏭️  Função init() já tem verificação\n')

# 4. Adicionar verificação após buscar o pedido
OLD_ORDER_FETCH = '''                if (orderResponse.ok) {
                    const order = await orderResponse.json();
                    console.log('Pedido completo:', order);
                    currentClientId = order.cliente_id;
                    console.log('currentClientId definido como:', currentClientId);
                }
            } catch (error) {
                console.error('Erro ao buscar dados do pedido:', error);
            }'''

NEW_ORDER_FETCH = '''                if (orderResponse.ok) {
                    const order = await orderResponse.json();
                    console.log('Pedido completo:', order);
                    currentClientId = order.cliente_id;
                    console.log('currentClientId definido como:', currentClientId);

                    // Verificar se cliente está ativo
                    if (!order.cliente_ativo) {
                        console.warn('Cliente inativo. Redirecionando para login.');
                        window.location.href = '/login';
                        return;
                    }
                } else {
                    console.warn('Pedido não encontrado. Redirecionando para login.');
                    window.location.href = '/login';
                    return;
                }
            } catch (error) {
                console.error('Erro ao buscar dados do pedido:', error);
                console.warn('Redirecionando para login devido ao erro.');
                window.location.href = '/login';
                return;
            }'''

if OLD_ORDER_FETCH in conteudo:
    conteudo = conteudo.replace(OLD_ORDER_FETCH, NEW_ORDER_FETCH)
    print('✅ Verificação de cliente ativo adicionada')
    print('   - Verifica se pedido existe')
    print('   - Verifica se cliente está ativo')
    print('   - Redireciona para /login em qualquer erro\n')
else:
    print('⏭️  Verificação de cliente já existe\n')

# Salvar arquivo
with open(arquivo, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print('═══════════════════════════════════════════════════════')
print('✅ CORREÇÕES CONCLUÍDAS!')
print('═══════════════════════════════════════════════════════')
print('\n🔐 AGORA O SISTEMA:')
print('\n   1. Redireciona para /login se não houver orderId')
print('   2. Redireciona para /login se pedido não for encontrado')
print('   3. Redireciona para /login se cliente estiver inativo')
print('   4. Redireciona para /login em caso de erro ao buscar pedido')
print('   5. Botão "Configuração do Agente" não redireciona mais')
print('\n❌ SEM MAIS ALERTS CHATOS!')
print('✅ REDIRECIONAMENTO AUTOMÁTICO PARA LOGIN!')
print('\n═══════════════════════════════════════════════════════\n')
