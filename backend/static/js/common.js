// ========================================
// KAIRIX - JavaScript Global
// Funções compartilhadas entre páginas
// ========================================

// Variáveis Globais
let currentOrder = null;
let currentConfig = null;

// ========================================
// AUTENTICAÇÃO E INICIALIZAÇÃO
// ========================================

// Carregar dados do painel
async function loadPanelData() {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            console.log('[DEBUG] Token não encontrado, mas redirect comentado');
            // window.location.href = '/login';
            return;
        }

        // Buscar dados do pedido
        const response = await fetch('/api/orders/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem('token');
                console.log('[DEBUG] 401 detectado, mas redirect comentado');
                // window.location.href = '/login';
                return;
            }
            throw new Error('Erro ao carregar dados');
        }

        currentOrder = await response.json();

        // Atualizar header do sidebar
        updateSidebarHeader();

        // Carregar configuração do bot
        await loadConfig();

    } catch (error) {
        console.error('Erro ao carregar dados do painel:', error);
    }
}

// Atualizar header do sidebar
function updateSidebarHeader() {
    if (!currentOrder) return;

    const productNameEl = document.getElementById('productName');
    const planNameEl = document.getElementById('planName');

    if (productNameEl) {
        productNameEl.textContent = currentOrder.plano?.nome || 'Kairix Bot';
    }

    if (planNameEl) {
        planNameEl.textContent = `Plano ${currentOrder.plano?.periodo || 'Mensal'}`;
    }
}

// Carregar configuração do bot
async function loadConfig() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/config/bot', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            currentConfig = await response.json();
            console.log('Configuração carregada:', currentConfig);
        }
    } catch (error) {
        console.error('Erro ao carregar configuração:', error);
    }
}

// ========================================
// MODALS
// ========================================

// Abrir modal Meus Dados
function openMyDataModal() {
    const modal = document.getElementById('myDataModal');
    if (modal) {
        modal.classList.add('active');
        loadMyData();
    }
}

// Fechar modal Meus Dados
function closeMyDataModal() {
    const modal = document.getElementById('myDataModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Carregar dados do cliente no modal
async function loadMyData() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/clients/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const client = await response.json();

            document.getElementById('clientNome').value = client.nome || '';
            document.getElementById('clientEmail').value = client.email || '';
            document.getElementById('clientTelefone').value = client.telefone || '';
            document.getElementById('clientEmpresa').value = client.nome_empresa || '';
            document.getElementById('clientCpfCnpj').value = client.cpf_cnpj || '';
            document.getElementById('clientWhatsapp').value = client.whatsapp || '';

            // Preencher campos de endereço se existirem
            if (document.getElementById('clientEndereco')) {
                document.getElementById('clientEndereco').value = client.endereco || '';
            }
            if (document.getElementById('clientCidade')) {
                document.getElementById('clientCidade').value = client.cidade || '';
            }
            if (document.getElementById('clientEstado')) {
                document.getElementById('clientEstado').value = client.estado || '';
            }
            if (document.getElementById('clientCep')) {
                document.getElementById('clientCep').value = client.cep || '';
            }
        }
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    }
}

// Salvar dados do cliente
async function saveMyData(event) {
    event.preventDefault();

    const btn = document.getElementById('saveMyDataBtn');
    const successMsg = document.getElementById('myDataSuccessMsg');
    const errorMsg = document.getElementById('myDataErrorMsg');

    btn.disabled = true;
    btn.textContent = 'Salvando...';
    successMsg.classList.remove('active');
    errorMsg.classList.remove('active');

    try {
        const token = localStorage.getItem('token');
        const data = {
            nome: document.getElementById('clientNome').value,
            email: document.getElementById('clientEmail').value,
            telefone: document.getElementById('clientTelefone').value,
            nome_empresa: document.getElementById('clientEmpresa').value,
            cpf_cnpj: document.getElementById('clientCpfCnpj').value,
            whatsapp: document.getElementById('clientWhatsapp').value
        };

        // Adicionar campos de endereço se existirem
        if (document.getElementById('clientEndereco')) {
            data.endereco = document.getElementById('clientEndereco').value;
        }
        if (document.getElementById('clientCidade')) {
            data.cidade = document.getElementById('clientCidade').value;
        }
        if (document.getElementById('clientEstado')) {
            data.estado = document.getElementById('clientEstado').value;
        }
        if (document.getElementById('clientCep')) {
            data.cep = document.getElementById('clientCep').value;
        }

        const response = await fetch('/api/clients/me', {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            successMsg.classList.add('active');
            setTimeout(() => {
                closeMyDataModal();
            }, 2000);
        } else {
            errorMsg.classList.add('active');
            errorMsg.textContent = 'Erro ao salvar dados. Tente novamente.';
        }
    } catch (error) {
        console.error('Erro ao salvar dados:', error);
        errorMsg.classList.add('active');
        errorMsg.textContent = 'Erro ao salvar dados. Tente novamente.';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Salvar Alterações';
    }
}

// Abrir modal Alterar Senha
function openChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    if (modal) {
        modal.classList.add('active');
        document.getElementById('changePasswordForm').reset();
    }
}

// Fechar modal Alterar Senha
function closeChangePasswordModal() {
    const modal = document.getElementById('changePasswordModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Alterar senha
async function changePassword(event) {
    event.preventDefault();

    const btn = document.getElementById('changePasswordBtn');
    const successMsg = document.getElementById('passwordSuccessMsg');
    const errorMsg = document.getElementById('passwordErrorMsg');

    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    successMsg.classList.remove('active');
    errorMsg.classList.remove('active');

    if (newPassword !== confirmPassword) {
        errorMsg.classList.add('active');
        errorMsg.textContent = 'As senhas não coincidem.';
        return;
    }

    if (newPassword.length < 6) {
        errorMsg.classList.add('active');
        errorMsg.textContent = 'A senha deve ter no mínimo 6 caracteres.';
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Alterando...';

    try {
        const token = localStorage.getItem('token');
        const response = await fetch('/api/clients/change-password', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (response.ok) {
            successMsg.classList.add('active');
            document.getElementById('changePasswordForm').reset();
            setTimeout(() => {
                closeChangePasswordModal();
            }, 2000);
        } else {
            const error = await response.json();
            errorMsg.classList.add('active');
            errorMsg.textContent = error.detail || 'Erro ao alterar senha.';
        }
    } catch (error) {
        console.error('Erro ao alterar senha:', error);
        errorMsg.classList.add('active');
        errorMsg.textContent = 'Erro ao alterar senha. Tente novamente.';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Alterar Senha';
    }
}

// ========================================
// MOBILE MENU
// ========================================

function toggleMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');
    const btn = document.getElementById('mobileMenuBtn');

    if (sidebar && overlay && btn) {
        sidebar.classList.toggle('mobile-open');
        overlay.classList.toggle('active');
        btn.classList.toggle('active');
    }
}

function closeMobileSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobileOverlay');
    const btn = document.getElementById('mobileMenuBtn');

    if (sidebar && overlay && btn) {
        sidebar.classList.remove('mobile-open');
        overlay.classList.remove('active');
        btn.classList.remove('active');
    }
}

// ========================================
// LOGOUT
// ========================================

async function logout() {
    if (confirm('Deseja realmente sair do painel?')) {
        try {
            // Chamar endpoint de logout para limpar cookie
            await fetch('/api/clients/logout', {
                method: 'POST',
                credentials: 'include'  // Importante para enviar cookies
            });

            // Limpar localStorage
            localStorage.clear();

            // Redirecionar para login
            window.location.href = '/login';
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
            // Mesmo com erro, limpar e redirecionar
            localStorage.clear();
            window.location.href = '/login';
        }
    }
}

// ========================================
// UTILITÁRIOS
// ========================================

// Formatar data
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// Formatar data/hora
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

// Formatar moeda
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Mostrar notificação toast
function showToast(message, type = 'success') {
    // Implementar toast notification
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ========================================
// HELPERS DE API
// ========================================

// Helper para fazer requisições autenticadas
async function fetchAuth(url, options = {}) {
    const token = localStorage.getItem('token');

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem('token');
        console.log('[DEBUG] 401 no fetch, mas redirect comentado');
        // window.location.href = '/login';
        throw new Error('Não autorizado');
    }

    return response;
}

// ========================================
// CONVERSAS - CARREGAMENTO DE DADOS
// ========================================

// Variáveis globais para conversas
let currentPedidoId = null;
let currentConversaId = null;

// Carregar lista de conversas
async function loadConversasSection(dataInicio = null, dataFim = null) {
    const container = document.getElementById('conversas-list-section');

    try {
        // Primeiro, buscar o pedido do cliente atual
        const ordersResponse = await fetch('/api/orders/me', {
            credentials: 'include'  // Importante para enviar cookies
        });

        if (!ordersResponse.ok) {
            throw new Error('Erro ao buscar pedidos');
        }

        const orders = await ordersResponse.json();

        if (!orders || orders.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 50px 20px; color: rgba(255,255,255,0.5);">
                    <div style="font-size: 48px; margin-bottom: 10px;">📋</div>
                    <p>Nenhum pedido encontrado.</p>
                </div>
            `;
            return;
        }

        // Usar o primeiro pedido (mais recente)
        currentPedidoId = orders[0].id;

        // Montar URL com filtros de data
        let url = `/api/conversas/pedido/${currentPedidoId}`;
        if (dataInicio && dataFim) {
            url += `?data_inicio=${dataInicio}&data_fim=${dataFim}`;
        }

        // Buscar conversas do pedido
        const conversasResponse = await fetch(url, {
            credentials: 'include'
        });

        if (!conversasResponse.ok) {
            throw new Error('Erro ao buscar conversas');
        }

        const conversas = await conversasResponse.json();

        if (!conversas || conversas.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 50px 20px; color: rgba(255,255,255,0.5);">
                    <div style="font-size: 48px; margin-bottom: 10px;">💬</div>
                    <p>Nenhuma conversa encontrada.</p>
                    <p style="font-size: 12px; margin-top: 10px;">As conversas aparecerão aqui quando seus clientes enviarem mensagens.</p>
                </div>
            `;
            return;
        }

        // Renderizar lista de conversas
        let html = '';
        conversas.forEach(conversa => {
            const dataFormatada = formatDateTime(conversa.criado_em);
            const statusClass = conversa.status === 'ativa' ? 'success' : 'pending';
            const totalMensagens = conversa.total_mensagens || 0;

            html += `
                <div class="conversa-item" data-conversa-id="${conversa.id}" onclick="selectConversa(${conversa.id})">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                        <div style="font-weight: 600; font-size: 14px;">${conversa.contato_nome || 'Sem nome'}</div>
                        <div style="display: flex; gap: 5px; align-items: center;">
                            <span class="badge" style="font-size: 10px; padding: 3px 8px; background: rgba(100, 100, 255, 0.2);">${totalMensagens} msg</span>
                            <span class="badge ${statusClass}" style="font-size: 10px; padding: 3px 8px;">${conversa.status}</span>
                        </div>
                    </div>
                    <div style="font-size: 12px; color: rgba(255,255,255,0.6); display: flex; justify-content: space-between; align-items: center;">
                        <span>📱 ${conversa.contato_numero}</span>
                        <span style="font-size: 11px; color: rgba(255,255,255,0.4);">🕐 ${dataFormatada}</span>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

    } catch (error) {
        console.error('Erro ao carregar conversas:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 50px 20px; color: rgba(255,90,90,0.7);">
                <div style="font-size: 48px; margin-bottom: 10px;">❌</div>
                <p>Erro ao carregar conversas.</p>
                <button onclick="loadConversasSection()" class="btn-primary" style="margin-top: 15px;">Tentar Novamente</button>
            </div>
        `;
    }
}

// Carregar mensagens de uma conversa
async function loadConversaMessages(conversaId) {
    currentConversaId = conversaId;

    const container = document.getElementById('mensagens-list-section');
    const tituloEl = document.getElementById('conversa-titulo-section');
    const infoEl = document.getElementById('conversa-info-section');

    try {
        // Buscar detalhes da conversa com mensagens
        const response = await fetch(`/api/conversas/${conversaId}`, {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao buscar mensagens');
        }

        const conversa = await response.json();

        // Atualizar título
        tituloEl.textContent = `💬 ${conversa.contato_nome || 'Sem nome'}`;
        infoEl.textContent = `📱 ${conversa.contato_numero} • Status: ${conversa.status}`;

        // Renderizar mensagens
        if (!conversa.mensagens || conversa.mensagens.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 50px 20px; color: rgba(255,255,255,0.5);">
                    <p>Nenhuma mensagem nesta conversa.</p>
                </div>
            `;
            return;
        }

        let html = '';
        conversa.mensagens.forEach(mensagem => {
            const isBot = mensagem.tipo === 'resposta';
            const dataFormatada = formatDateTime(mensagem.criado_em);

            html += `
                <div style="display: flex; justify-content: ${isBot ? 'flex-start' : 'flex-end'}; margin-bottom: 15px;">
                    <div style="max-width: 70%; padding: 12px 16px; border-radius: 12px; background: ${isBot ? 'rgba(99, 102, 241, 0.1)' : 'rgba(16, 185, 129, 0.1)'}; border: 1px solid ${isBot ? 'rgba(99, 102, 241, 0.3)' : 'rgba(16, 185, 129, 0.3)'};">
                        <div style="font-size: 10px; color: rgba(255,255,255,0.5); margin-bottom: 5px;">
                            ${isBot ? '🤖 Bot' : '👤 Cliente'} • ${dataFormatada}
                        </div>
                        <div style="font-size: 14px; line-height: 1.5; white-space: pre-wrap;">
                            ${mensagem.conteudo}
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;

        // Scroll para o final
        container.scrollTop = container.scrollHeight;

    } catch (error) {
        console.error('Erro ao carregar mensagens:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 50px 20px; color: rgba(255,90,90,0.7);">
                <p>Erro ao carregar mensagens.</p>
            </div>
        `;
    }
}

// Filtrar conversas por data
async function filtrarConversasPorData() {
    const dataInicio = document.getElementById('data-inicio-conversas').value;
    const dataFim = document.getElementById('data-fim-conversas').value;

    if (!dataInicio || !dataFim) {
        alert('Por favor, selecione ambas as datas.');
        return;
    }

    await loadConversasSection(dataInicio, dataFim);
}

// Limpar filtro de conversas
function limparFiltroConversas() {
    document.getElementById('data-inicio-conversas').value = '';
    document.getElementById('data-fim-conversas').value = '';
    loadConversasSection();
}

// ========================================
// PASSWORD VISIBILITY TOGGLE
// ========================================

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '🙈';
    } else {
        input.type = 'password';
        icon.textContent = '👁️';
    }
}

// Selecionar conversa e marcar como ativa
function selectConversa(conversaId) {
    // Remover classe 'active' de todas as conversas
    document.querySelectorAll('.conversa-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Adicionar classe 'active' na conversa clicada
    const conversaElement = document.querySelector(`.conversa-item[data-conversa-id="${conversaId}"]`);
    if (conversaElement) {
        conversaElement.classList.add('active');
    }
    
    // Carregar mensagens da conversa
    loadConversaMessages(conversaId);
}

// ========================================
//  ATUALIZAR BADGES DO MENU
// ========================================

async function updateMenuBadges() {
    try {
        const response = await fetch('/api/orders/me', { credentials: 'include' });
        if (!response.ok) return;
        
        const orders = await response.json();
        if (!orders || orders.length === 0) return;
        
        const pedidoId = orders[0].id;
        
        // Atualizar badge de conversas
        const conversasResponse = await fetch(`/api/conversas/pedido/${pedidoId}`, { credentials: 'include' });
        if (conversasResponse.ok) {
            const conversas = await conversasResponse.json();
            const badgeConversas = document.getElementById('badge-conversas');
            if (badgeConversas) {
                badgeConversas.textContent = conversas.length;
            }
        }
        
        // Atualizar badge de respostas
        const respostasResponse = await fetch(`/api/config/${pedidoId}/respostas`, { credentials: 'include' });
        if (respostasResponse.ok) {
            const respostas = await respostasResponse.json();
            const badgeRespostas = document.getElementById('badge-respostas');
            if (badgeRespostas && Array.isArray(respostas)) {
                badgeRespostas.textContent = respostas.length;
            }
        }
        
        // Atualizar badge de base de conhecimento
        const docResponse = await fetch(`/api/knowledge/list/${pedidoId}`, { credentials: 'include' });
        if (docResponse.ok) {
            const docData = await docResponse.json();
            const badgeDocs = document.getElementById('badge-base-conhecimento');
            if (badgeDocs && docData.documents) {
                badgeDocs.textContent = docData.documents.length;
            }
        }
        
        // Atualizar badge de atendentes
        const atendentesResponse = await fetch(`/api/config/${pedidoId}/atendentes`, { credentials: 'include' });
        if (atendentesResponse.ok) {
            const atendentes = await atendentesResponse.json();
            const badgeAtendentes = document.getElementById('badge-atendentes');
            if (badgeAtendentes && Array.isArray(atendentes)) {
                badgeAtendentes.textContent = atendentes.length;
            }
        }
        
    } catch (error) {
        console.error('[DEBUG] Erro ao atualizar badges:', error);
    }
}

// Atualizar badges quando a página carrega
document.addEventListener('DOMContentLoaded', updateMenuBadges);
