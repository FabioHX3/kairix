"""
Router para integração com Evolution API
Gerencia webhooks, envio de mensagens e processamento inteligente
"""
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, Optional, List
import httpx
import json
from datetime import datetime
import re
import unicodedata
import models
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/api/evolution", tags=["evolution"])


# ============ FUNÇÕES AUXILIARES ============

def normalize_text(text: str) -> str:
    """Remove acentos e normaliza texto para busca inteligente"""
    if not text:
        return ""
    # Normalizar unicode e remover acentos
    nfkd = unicodedata.normalize('NFD', text.lower())
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def extract_phone_number(data: Dict) -> str:
    """Extrai número de telefone do webhook"""
    try:
        if 'key' in data and 'remoteJid' in data['key']:
            return data['key']['remoteJid'].split('@')[0]
        if 'from' in data:
            return data['from'].split('@')[0]
        return None
    except:
        return None


def extract_message_text(data: Dict) -> str:
    """Extrai texto da mensagem do webhook"""
    try:
        if 'message' in data:
            msg = data['message']
            if 'conversation' in msg:
                return msg['conversation']
            if 'extendedTextMessage' in msg:
                return msg['extendedTextMessage'].get('text', '')
            if 'imageMessage' in msg and 'caption' in msg['imageMessage']:
                return msg['imageMessage']['caption']
        return ""
    except:
        return ""


def get_greeting_by_time() -> str:
    """Retorna saudação apropriada baseada no horário"""
    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Bom dia"
    elif 12 <= hour < 18:
        return "Boa tarde"
    else:
        return "Boa noite"


def remove_emojis(text: str) -> str:
    """Remove emojis e símbolos especiais de um texto"""
    import re
    # Remove emojis e símbolos Unicode (incluindo ℹ️ ✅ ❌ ⚠️ etc)
    emoji_pattern = re.compile("["
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F700-\U0001F77F"  # alchemical symbols
        u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA00-\U0001FA6F"  # Chess Symbols
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2100-\u214F"  # Letterlike Symbols (inclui ℹ)
        u"\u2190-\u21FF"  # Arrows
        u"\u2600-\u26FF"  # Miscellaneous Symbols
        u"\u2700-\u27BF"  # Dingbats
        u"\u200d"
        u"\ufe0f"  # variation selector
        u"\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text).strip()


def gerar_menu_com_pergunta_rapida(menu_opcoes: list, titulo: str = "Menu Principal") -> str:
    """Gera menu com opção de pergunta rápida no final"""
    texto = f"*{titulo}*\n\n"

    for opcao in menu_opcoes:
        numero = opcao.get('numero', '')
        titulo_opcao = remove_emojis(opcao.get('titulo', ''))
        texto += f"{numero}. {titulo_opcao}\n"

    # Adicionar opção de pergunta rápida
    # Pegar o próximo número disponível
    numeros_usados = [int(op.get('numero', 0)) for op in menu_opcoes if op.get('numero', '').isdigit()]
    proximo_numero = max(numeros_usados) + 1 if numeros_usados else len(menu_opcoes) + 1
    texto += f"{proximo_numero}. Fazer uma pergunta rápida\n"

    return texto, proximo_numero


def generate_welcome_message(name: str, pedido: models.Pedido) -> str:
    """Gera mensagem de boas-vindas personalizada com menu"""
    greeting = get_greeting_by_time()

    # Obter configuração do pedido
    config = {}
    menu_opcoes = []
    if pedido.configuracao_agente:
        try:
            config = json.loads(pedido.configuracao_agente)
            menu_opcoes = config.get('menu', [])
        except:
            pass

    # Mensagem inicial
    message = f"{greeting}, {name}!\n\n"
    message += f"Como posso ajudar você hoje?\n\n"

    # Adicionar menu se configurado
    if menu_opcoes:
        menu_texto, _ = gerar_menu_com_pergunta_rapida(menu_opcoes)
        message += menu_texto
    else:
        message += f"Digite *menu* para ver nossas opções."

    return message


async def send_whatsapp_message(
    evolution_url: str,
    evolution_key: str,
    instance_name: str,
    phone: str,
    message: str
) -> bool:
    """Envia mensagem via Evolution API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{evolution_url}/message/sendText/{instance_name}",
                headers={
                    "apikey": evolution_key,
                    "Content-Type": "application/json"
                },
                json={
                    "number": phone,
                    "text": message
                }
            )
            return response.status_code in [200, 201]
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")
        return False


async def send_whatsapp_list(
    evolution_url: str,
    evolution_key: str,
    instance_name: str,
    phone: str,
    title: str,
    description: str,
    button_text: str,
    sections: List[Dict]
) -> bool:
    """Envia mensagem com lista interativa via Evolution API"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{evolution_url}/message/sendList/{instance_name}",
                headers={
                    "apikey": evolution_key,
                    "Content-Type": "application/json"
                },
                json={
                    "number": phone,
                    "title": title,
                    "description": description,
                    "buttonText": button_text,
                    "footerText": "Kairix Bot",
                    "sections": sections
                }
            )
            return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar lista: {e}")
        return False


async def send_whatsapp_menu(
    evolution_url: str,
    evolution_key: str,
    instance_name: str,
    phone: str,
    message: str,
    options: List[Dict]
) -> bool:
    """Envia mensagem com botões/menu via Evolution API"""
    try:
        buttons = []
        for idx, opt in enumerate(options[:3], 1):  # Evolution limita a 3 botões
            buttons.append({
                "buttonId": str(opt.get('id', idx)),
                "buttonText": {"displayText": opt.get('texto', f'Opção {idx}')},
                "type": 1
            })

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{evolution_url}/message/sendButtons/{instance_name}",
                headers={
                    "apikey": evolution_key,
                    "Content-Type": "application/json"
                },
                json={
                    "number": phone,
                    "title": "Menu",
                    "description": message,
                    "buttons": buttons,
                    "footerText": "Kairix Bot"
                }
            )
            return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar menu: {e}")
        return False


async def notify_attendants(
    config: models.ConfiguracaoBot,
    customer_name: str,
    customer_phone: str,
    conversa_id: int
):
    """Envia notificação via WhatsApp para atendentes configurados"""
    try:
        # Verificar se há atendentes configurados
        if not config.numeros_atendentes:
            print("⚠️ Nenhum atendente configurado")
            return

        # Parsear números de atendentes
        atendentes = json.loads(config.numeros_atendentes) if isinstance(config.numeros_atendentes, str) else []

        if not atendentes:
            print("⚠️ Lista de atendentes vazia")
            return

        # Mensagem de notificação
        mensagem = f"""🔔 *Nova Solicitação de Atendimento*

👤 Cliente: {customer_name}
📱 Número: {customer_phone}
🆔 Conversa ID: {conversa_id}

⏰ {datetime.now().strftime("%d/%m/%Y %H:%M")}

_O cliente está aguardando atendimento humano._"""

        # Enviar para cada atendente
        for numero_atendente in atendentes:
            try:
                print(f"📤 Enviando notificação para atendente: {numero_atendente}")
                await send_whatsapp_message(
                    evolution_url=config.evolution_url,
                    evolution_key=config.evolution_key,
                    instance_name=config.evolution_instance,
                    phone=numero_atendente,
                    message=mensagem
                )
                print(f"✅ Notificação enviada para {numero_atendente}")
            except Exception as e:
                print(f"❌ Erro ao notificar {numero_atendente}: {e}")

    except Exception as e:
        print(f"❌ Erro ao processar notificação de atendentes: {e}")


# ============ PROCESSADOR DE MENSAGENS ============

async def process_message(
    phone: str,
    message_text: str,
    config: models.ConfiguracaoBot,
    pedido: models.Pedido,
    conversa: models.Conversa,
    db: Session
) -> Optional[str]:
    """Processa mensagem e retorna resposta baseada na configuração"""

    normalized_input = normalize_text(message_text)

    # Carregar menu da configuração do pedido
    menu_opcoes = []
    if pedido.configuracao_agente:
        try:
            config_data = json.loads(pedido.configuracao_agente)
            menu_opcoes = config_data.get('menu', [])
        except:
            pass

    # Carregar contexto da conversa
    contexto = {}
    if conversa.contexto:
        try:
            contexto = json.loads(conversa.contexto)
        except:
            contexto = {}

    # ANTES DE QUALQUER COISA: Verificar saudações
    saudacoes = ['oi', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'opa', 'olá', 'eai', 'e ai']
    for saudacao in saudacoes:
        saudacao_norm = normalize_text(saudacao)
        if saudacao_norm == normalized_input or normalized_input.startswith(saudacao_norm):
            greeting = get_greeting_by_time()
            # Limpar contexto
            contexto = {}
            crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
                contexto=json.dumps(contexto)
            ))
            # Mostrar menu com saudação
            if menu_opcoes:
                menu_texto, _ = gerar_menu_com_pergunta_rapida(menu_opcoes)
                return f"{greeting}! 👋\n\nComo posso ajudar você?\n\n{menu_texto}"
            return f"{greeting}! 👋\n\nComo posso ajudar você?\n\nDigite *menu* para ver as opções disponíveis."

    # Verificar comando "voltar" ou "menu" (SEMPRE volta ao menu principal)
    if 'voltar' in normalized_input or 'menu' in normalized_input:
        # Limpar contexto
        contexto = {}
        crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
            contexto=json.dumps(contexto)
        ))

        # Mostrar menu principal com opção de pergunta rápida
        if menu_opcoes:
            menu_texto, _ = gerar_menu_com_pergunta_rapida(menu_opcoes)
            return menu_texto
        return "Menu não configurado."

    # SEMPRE VERIFICAR RESPOSTAS RÁPIDAS (independente do modo)
    respostas_rapidas = []
    if pedido.configuracao_agente:
        try:
            config_data = json.loads(pedido.configuracao_agente)
            respostas_rapidas = config_data.get('respostas', [])
        except:
            pass

    if respostas_rapidas:
        for resposta in respostas_rapidas:
            palavras_chave = resposta.get('palavras_chave', [])
            resposta_texto = resposta.get('resposta', '')

            for palavra in palavras_chave:
                palavra_norm = normalize_text(palavra)
                if palavra_norm in normalized_input or normalized_input in palavra_norm:
                    # Responder com opções de navegação
                    resposta_completa = f"{resposta_texto}\n\n"
                    resposta_completa += f"━━━━━━━━━━━━━━━━━\n"
                    resposta_completa += f"Digite *menu* para voltar ao menu principal\n"
                    resposta_completa += f"Ou faça outra pergunta rápida!"
                    return resposta_completa

    # VERIFICAR SE ESTÁ EM UM SUBMENU ATIVO
    submenu_ativo = contexto.get('submenu_ativo')
    if submenu_ativo:
        # Processar escolha do submenu
        submenu_opcoes = submenu_ativo.get('opcoes', [])

        # Verificar se escolheu a opção "Pergunta Rápida" do submenu
        numeros_usados = [int(op.get('numero', 0)) for op in submenu_opcoes if op.get('numero', '').isdigit()]
        numero_pergunta_rapida = max(numeros_usados) + 1 if numeros_usados else len(submenu_opcoes) + 1

        if str(numero_pergunta_rapida) in message_text or ('pergunta' in normalized_input and 'rapida' in normalized_input):
            # Limpar submenu e ativar modo pergunta rápida
            contexto.pop('submenu_ativo', None)
            contexto['modo_pergunta_rapida'] = True
            crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
                contexto=json.dumps(contexto)
            ))
            return "❓ *Modo Pergunta Rápida ativado!*\n\nPode fazer suas perguntas que vou responder o que souber.\n\n_Digite *menu* para voltar ao menu principal_"

        for sub_opcao in submenu_opcoes:
            numero = str(sub_opcao.get('numero', ''))
            titulo = sub_opcao.get('titulo', '')

            # Se escolheu uma opção do submenu
            if numero in message_text or normalize_text(titulo) in normalized_input:
                resposta = sub_opcao.get('resposta', 'Opção selecionada!')

                # Manter submenu ativo para permitir novas escolhas
                # Não limpar o contexto - assim o usuário pode escolher outras opções do mesmo submenu

                # Adicionar instruções de navegação
                submenu_titulo = submenu_ativo.get('titulo', 'Menu')
                resposta_completa = f"{resposta}\n\n"
                resposta_completa += f"━━━━━━━━━━━━━━━━━\n"
                resposta_completa += f"Digite *voltar* para retornar ao submenu {submenu_titulo}\n"
                resposta_completa += f"Digite *menu* para voltar ao menu principal"

                return resposta_completa

        # Se não escolheu nenhuma opção válida, informar
        submenu_titulo = submenu_ativo.get('titulo', 'submenu')
        return f"⚠️ Opção inválida.\n\nPor favor, escolha uma das opções do {submenu_titulo} ou:\n• Digite *voltar* para ver as opções novamente\n• Digite *menu* para voltar ao menu principal"

    # 2. Verificar se escolheu a opção "Pergunta Rápida"
    if menu_opcoes:
        # Calcular o número da opção "pergunta rápida"
        numeros_usados = [int(op.get('numero', 0)) for op in menu_opcoes if op.get('numero', '').isdigit()]
        numero_pergunta_rapida = max(numeros_usados) + 1 if numeros_usados else len(menu_opcoes) + 1

        if str(numero_pergunta_rapida) in message_text or 'pergunta' in normalized_input and 'rapida' in normalized_input:
            # Ativar modo pergunta rápida
            contexto['modo_pergunta_rapida'] = True
            crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
                contexto=json.dumps(contexto)
            ))
            return "❓ *Modo Pergunta Rápida ativado!*\n\nPode fazer suas perguntas que vou responder o que souber.\n\n_Digite *menu* para voltar ao menu principal_"

    # 3. Verificar menu interativo principal
    for opcao in menu_opcoes:
        numero = str(opcao.get('numero', ''))
        titulo = opcao.get('titulo', '')
        acao = opcao.get('acao', 'resposta')

        # Se escolheu esta opção
        if numero in message_text or normalize_text(titulo) in normalized_input:

            if acao == 'resposta':
                resposta = opcao.get('resposta', opcao.get('descricao', ''))
                # Adicionar opções de navegação
                resposta_completa = f"{resposta}\n\n"
                resposta_completa += f"━━━━━━━━━━━━━━━━━\n"
                resposta_completa += f"Digite *menu* para voltar ao menu principal\n"
                resposta_completa += f"Ou faça uma pergunta rápida sobre qualquer assunto!"
                return resposta_completa

            elif acao == 'submenu':
                # Carregar submenu
                submenu_json = opcao.get('submenu', '[]')
                try:
                    submenu = json.loads(submenu_json) if isinstance(submenu_json, str) else submenu_json

                    if submenu:
                        # Salvar submenu no contexto
                        contexto['submenu_ativo'] = {
                            'titulo': titulo,
                            'opcoes': submenu
                        }
                        crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
                            contexto=json.dumps(contexto)
                        ))

                        # Retornar opções do submenu com pergunta rápida
                        menu_texto, _ = gerar_menu_com_pergunta_rapida(submenu, titulo)
                        return f"{menu_texto}\n_Digite 'voltar' para retornar ao menu principal_"
                except:
                    return "Erro ao carregar submenu."

            elif acao == 'atendente':
                # Mudar status da conversa para AGUARDANDO
                crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
                    status=models.StatusConversa.AGUARDANDO
                ))

                # Enviar notificação para atendentes (se configurados)
                await notify_attendants(
                    config=config,
                    customer_name=conversa.contato_nome,
                    customer_phone=conversa.contato_numero,
                    conversa_id=conversa.id
                )

                return "Um atendente será notificado e entrará em contato em breve. Aguarde um momento..."

    # 4. Se tem IA ativa (Bot IA ou Agente Financeiro)
    plano_tipo = pedido.plano.tipo if pedido and pedido.plano else None

    if plano_tipo in ['bot_ia', 'agente_financeiro']:
        return await process_with_ai(message_text, config, plano_tipo, db)

    # 5. Resposta padrão se não encontrou nada
    return config.mensagem_nao_entendida or "❓ Desculpe, não entendi. Digite *menu* para ver as opções disponíveis."


async def process_with_ai(
    message: str,
    config: models.ConfiguracaoBot,
    plano_tipo: str,
    db: Session
) -> str:
    """Processa mensagem com IA (para planos Bot IA e Agente Financeiro)"""

    # TODO: Implementar integração com OpenAI/Claude
    # TODO: Buscar documentos vetorizados relacionados
    # TODO: Para Agente Financeiro, incluir contexto financeiro

    # Por enquanto, resposta placeholder
    if plano_tipo == 'agente_financeiro':
        return "🤖 [IA Financeira] Processando sua solicitação com contexto financeiro..."
    else:
        return "🤖 [IA] Processando sua mensagem com inteligência artificial..."


# ============ WEBHOOK RECEIVER ============

async def process_webhook_background(pedido_id: int, data: dict, config, pedido):
    """Processa webhook em background para resposta rápida"""
    print(f"🚨 BACKGROUND TASK CHAMADA! Pedido: {pedido_id}")

    # Criar nova sessão de banco para o background task
    from database import SessionLocal
    db = SessionLocal()

    try:
        print(f"🔍 DEBUG: Iniciando process_webhook_background para pedido {pedido_id}")

        # Verificar se é mensagem
        event_type = data.get('event', '')
        print(f"🔍 DEBUG: event_type = {event_type}")

        if event_type not in ['messages.upsert', 'message.create']:
            print(f"⏭️ Evento ignorado: {event_type}")
            return

        # Extrair informações
        # SEMPRE extrair phone do data.key.remoteJid (número do cliente)
        phone = extract_phone_number(data.get('data', {}))
        if not phone:
            # Fallback: tentar campo 'sender' na raiz do webhook
            phone = data.get('sender', '').split('@')[0] if data.get('sender') else None

        message_text = extract_message_text(data.get('data', {}))
        print(f"🔍 DEBUG: phone={phone}, message_text={message_text}")

        if not phone or not message_text:
            print(f"⏭️ Mensagem sem phone ou texto")
            return

        # Verificar se é mensagem do próprio bot (evitar loop)
        from_me = data.get('data', {}).get('key', {}).get('fromMe', False)
        print(f"🔍 DEBUG: fromMe={from_me}")
        if from_me:
            print(f"⏭️ Mensagem do próprio bot ignorada")
            return

        print(f"✅ Mensagem válida - iniciando processamento")

        # FILTRO: Responder apenas para o número específico
        # NUMERO_PERMITIDO = "556599342609"
        # if phone != NUMERO_PERMITIDO:
        #     print(f"⏭️ Mensagem ignorada - Número não permitido: {phone}")
        #     return

        # === GRAVAR CONVERSA E MENSAGEM ===

        # 1. Buscar ou criar conversa
        conversa = crud.get_conversa_by_numero(db, pedido_id, phone)

        if not conversa:
            # Extrair nome do contato
            push_name = data.get('data', {}).get('pushName', phone)
            remote_jid = data.get('data', {}).get('key', {}).get('remoteJid', '')

            # Criar nova conversa
            conversa_data = schemas.ConversaCriar(
                pedido_id=pedido_id,
                contato_nome=push_name,
                contato_numero=phone,
                evolution_remote_jid=remote_jid,
                evolution_instance=config.evolution_instance
            )
            conversa = crud.create_conversa(db, conversa_data)

            # Marcar como primeira mensagem
            # Cada tipo de agente vai cuidar da própria mensagem de boas-vindas
            is_first_message = True
        else:
            is_first_message = False

        # Se conversa estava AGUARDANDO, reativar automaticamente
        if conversa.status == models.StatusConversa.AGUARDANDO:
            print(f"🔄 Reativando conversa que estava aguardando atendente")
            crud.update_conversa(db, conversa.id, schemas.ConversaAtualizar(
                status=models.StatusConversa.ATIVA
            ))
            conversa = crud.get_conversa_by_numero(db, pedido_id, phone)  # Recarregar

        # 2. Gravar mensagem recebida
        msg_id = data.get('data', {}).get('key', {}).get('id', None) or None

        # Salvar conversa_id ANTES de qualquer operação que possa dar erro
        conversa_id = conversa.id

        mensagem_recebida = schemas.MensagemCriar(
            conversa_id=conversa_id,
            tipo=schemas.TipoMensagem.TEXTO,
            direcao=schemas.DirecaoMensagem.RECEBIDA,
            conteudo=message_text,
            evolution_message_id=msg_id,
            evolution_push_name=data.get('data', {}).get('pushName', ''),
            respondida_por_bot=True
        )

        try:
            msg_recebida_db = crud.create_mensagem(db, mensagem_recebida)
            timestamp_recebida = msg_recebida_db.timestamp
        except Exception as e:
            # Se der erro de unique constraint no evolution_message_id, é porque o webhook veio duplicado
            # Nesse caso busca a resposta já enviada e reenvia
            if "evolution_message_id" in str(e) and "unique" in str(e).lower():
                print(f"🔄 WEBHOOK DUPLICADO: mensagem {msg_id} já foi processada")
                # Rollback para limpar o erro da sessão
                db.rollback()

                # Buscar a mensagem já processada no banco
                mensagem_existente = db.query(models.Mensagem).filter(
                    models.Mensagem.evolution_message_id == msg_id
                ).first()

                if mensagem_existente:
                    # Buscar a resposta que foi enviada logo após essa mensagem
                    resposta_anterior = db.query(models.Mensagem).filter(
                        models.Mensagem.conversa_id == mensagem_existente.conversa_id,
                        models.Mensagem.direcao == models.DirecaoMensagem.ENVIADA,
                        models.Mensagem.timestamp > mensagem_existente.timestamp
                    ).order_by(models.Mensagem.timestamp.asc()).first()

                    if resposta_anterior:
                        print(f"💾 Reenviando resposta do cache: {resposta_anterior.conteudo[:100]}...")
                        # Reenviar a mesma resposta sem chamar a IA
                        await send_whatsapp_message(
                            evolution_url=config.evolution_url,
                            evolution_key=config.evolution_key,
                            instance_name=config.evolution_instance,
                            phone=phone,
                            message=resposta_anterior.conteudo
                        )
                        return
                    else:
                        print(f"⚠️ Resposta anterior não encontrada, ignorando webhook duplicado")
                        return
                else:
                    print(f"⚠️ Mensagem existente não encontrada, ignorando webhook duplicado")
                    return
            else:
                raise e

        # 3. DETECTAR TIPO DE AGENTE (fazer isso ANTES de verificar primeira mensagem)
        if pedido.plano.tipo == models.TipoPlano.AGENTE_IA:
            # === AGENTE IA COM RAG ===
            print(f"🤖 Usando Agente IA com RAG para pedido {pedido_id}")

            from services.ia_handler import IAHandler

            ia_handler = IAHandler()

            # VERIFICAR SE PRECISA ENVIAR BOAS-VINDAS
            # Se última mensagem foi há mais de 10 minutos, enviar boas-vindas
            from datetime import datetime, timedelta
            enviar_boas_vindas = False

            if is_first_message:
                enviar_boas_vindas = True
                print(f"👋 Primeira mensagem - enviando boas-vindas")
            else:
                # Verificar última mensagem da conversa
                ultima_mensagem = db.query(models.Mensagem)\
                    .filter(models.Mensagem.conversa_id == conversa_id)\
                    .order_by(models.Mensagem.timestamp.desc())\
                    .first()

                if ultima_mensagem:
                    tempo_decorrido = datetime.now() - ultima_mensagem.timestamp
                    if tempo_decorrido > timedelta(minutes=10):
                        enviar_boas_vindas = True
                        print(f"👋 Última mensagem há {tempo_decorrido.seconds//60} minutos - enviando boas-vindas")

            # Enviar boas-vindas se necessário (MENSAGEM FIXA, SEM RAG)
            if enviar_boas_vindas:
                welcome_text = """👋 Olá! Seja bem-vindo!

Sou o assistente inteligente e estou aqui para ajudar você com suas dúvidas.

Você pode enviar suas perguntas por texto ou áudio.

📌 Para falar com um atendente humano, digite *atendente* a qualquer momento.

Como posso ajudar você hoje?"""

                await send_whatsapp_message(
                    evolution_url=config.evolution_url,
                    evolution_key=config.evolution_key,
                    instance_name=config.evolution_instance,
                    phone=phone,
                    message=welcome_text
                )

                # Gravar mensagem de boas-vindas
                welcome_msg = schemas.MensagemCriar(
                    conversa_id=conversa_id,
                    tipo=schemas.TipoMensagem.TEXTO,
                    direcao=schemas.DirecaoMensagem.ENVIADA,
                    conteudo=welcome_text,
                    respondida_por_bot=True
                )
                crud.create_mensagem(db, welcome_msg)
                print(f"✅ Boas-vindas enviadas")

            # Preparar configurações do bot
            bot_config = {
                "numeros_atendentes": config.numeros_atendentes if config.numeros_atendentes else []
            }

            # Processar mensagem com IA
            success = await ia_handler.handle_message(
                instance_name=config.evolution_instance,
                message_data=data.get('data', {}),
                config=bot_config
            )

            # Mensagem já foi enviada pelo handler de IA
            # Retornar para não processar novamente
            return

        # === AGENTE NORMAL (código existente) ===

        # Para Agente Normal: enviar boas-vindas se for primeira mensagem
        if is_first_message:
            print(f"👋 Enviando boas-vindas do Agente Normal...")
            push_name = data.get('data', {}).get('pushName', phone)
            welcome_message = generate_welcome_message(push_name, pedido)

            await send_whatsapp_message(
                evolution_url=config.evolution_url,
                evolution_key=config.evolution_key,
                instance_name=config.evolution_instance,
                phone=phone,
                message=welcome_message
            )

            # Gravar mensagem de boas-vindas
            welcome_msg = schemas.MensagemCriar(
                conversa_id=conversa.id,
                tipo=schemas.TipoMensagem.TEXTO,
                direcao=schemas.DirecaoMensagem.ENVIADA,
                conteudo=welcome_message,
                respondida_por_bot=True
            )
            crud.create_mensagem(db, welcome_msg)

            # Para o Agente Normal, não processar a primeira mensagem
            # (usuário deve escolher opção do menu)
            print(f"⏭️ Primeira mensagem do Agente Normal - aguardando escolha do menu")
            return

        response_text = await process_message(
            phone=phone,
            message_text=message_text,
            config=config,
            pedido=pedido,
            conversa=conversa,
            db=db
        )

        # 4. Enviar resposta
        if response_text:
            # Calcular tempo de resposta ANTES de enviar
            timestamp_enviada = datetime.utcnow()
            tempo_resposta = (timestamp_enviada - timestamp_recebida).total_seconds()

            # Tentar enviar mensagem
            success = await send_whatsapp_message(
                evolution_url=config.evolution_url,
                evolution_key=config.evolution_key,
                instance_name=config.evolution_instance,
                phone=phone,
                message=response_text
            )

            # 5. Gravar resposta enviada (SEMPRE, mesmo se falhou o envio)
            # Isso garante histórico completo e permite testes sem Evolution configurado
            print(f"💾 Salvando resposta do bot - Conversa: {conversa.id}, Texto: {response_text[:50]}...")

            mensagem_enviada = schemas.MensagemCriar(
                conversa_id=conversa.id,
                tipo=schemas.TipoMensagem.TEXTO,
                direcao=schemas.DirecaoMensagem.ENVIADA,
                conteudo=response_text,
                respondida_por_bot=True,
                tempo_resposta=tempo_resposta
            )

            msg_salva = crud.create_mensagem(db, mensagem_enviada)
            print(f"✅ Mensagem do bot salva com ID: {msg_salva.id}, Direção: {msg_salva.direcao}")

            # 6. Atualizar tempo da primeira resposta se necessário
            if not conversa.tempo_primeira_resposta:
                crud.update_conversa(
                    db,
                    conversa.id,
                    schemas.ConversaAtualizar(contexto=conversa.contexto)
                )
                # Atualizar manualmente o tempo_primeira_resposta
                conversa.tempo_primeira_resposta = tempo_resposta
                db.commit()

    except Exception as e:
        print(f"❌ Erro processando webhook em background: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Fechar a sessão do banco
        db.close()


@router.post("/webhook/{pedido_id}")
async def receive_webhook(
    pedido_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Recebe webhooks do Evolution API - RESPOSTA RÁPIDA
    URL para configurar no Evolution: https://seu-dominio.com/api/evolution/webhook/{pedido_id}
    """
    try:
        print(f"\n{'='*80}")
        print(f"🔔 WEBHOOK RECEBIDO - Pedido ID: {pedido_id}")
        print(f"{'='*80}")

        # Buscar pedido e configuração RAPIDAMENTE (carregar relacionamento plano)
        pedido = db.query(models.Pedido).options(joinedload(models.Pedido.plano)).filter(models.Pedido.id == pedido_id).first()
        if not pedido:
            print(f"❌ Pedido {pedido_id} não encontrado!")
            return {"status": "error", "message": "Pedido não encontrado"}

        # Buscar configuração do bot
        config = db.query(models.ConfiguracaoBot).filter(
            models.ConfiguracaoBot.pedido_id == pedido_id
        ).first()

        if not config or not config.evolution_url or not config.evolution_key:
            print(f"⚠️ Evolution não configurado para pedido {pedido_id}")
            return {"status": "error", "message": "Evolution não configurado"}

        # Parse do webhook
        data = await request.json()

        # Log COMPLETO do webhook
        print(f"📦 Dados recebidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print(f"{'='*80}\n")

        # PROCESSAR DIRETAMENTE (sem background por enquanto para debug)
        await process_webhook_background(pedido_id, data, config, pedido)

        # Retornar resposta
        return {"status": "received", "pedido_id": pedido_id}

    except Exception as e:
        print(f"❌ Erro recebendo webhook: {e}")
        return {"status": "error", "message": str(e)}


# ============ CONFIGURAÇÃO EVOLUTION ============

@router.post("/config/{pedido_id}")
async def save_evolution_config(
    pedido_id: int,
    config_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Salva configuração do Evolution API para um pedido"""

    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar ou criar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config:
        config = models.ConfiguracaoBot(pedido_id=pedido_id)
        db.add(config)

    # Atualizar apenas os campos que foram enviados (não sobrescrever com None)
    if 'evolution_url' in config_data and config_data.get('evolution_url'):
        config.evolution_url = config_data.get('evolution_url')

    if 'evolution_key' in config_data and config_data.get('evolution_key'):
        config.evolution_key = config_data.get('evolution_key')

    if 'evolution_instance' in config_data and config_data.get('evolution_instance'):
        config.evolution_instance = config_data.get('evolution_instance')

    # Atualizar atendentes se fornecido
    if 'numeros_atendentes' in config_data:
        config.numeros_atendentes = config_data.get('numeros_atendentes')

    config.atualizado_em = datetime.utcnow()

    db.commit()
    db.refresh(config)

    # Retornar URL do webhook para configurar no Evolution
    webhook_url = f"{config_data.get('kairix_url', 'https://seu-dominio.com')}/api/evolution/webhook/{pedido_id}"

    return {
        "message": "Configuração salva com sucesso",
        "webhook_url": webhook_url,
        "instrucoes": [
            "1. Acesse seu painel Evolution API",
            "2. Vá em Configurações > Webhooks",
            f"3. Configure a URL: {webhook_url}",
            "4. Ative os eventos: messages.upsert",
            "5. Teste enviando uma mensagem para o número conectado"
        ]
    }


@router.get("/config/{pedido_id}")
async def get_evolution_config(pedido_id: int, db: Session = Depends(get_db)):
    """Busca configuração Evolution de um pedido"""

    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config:
        return {
            "configured": False,
            "evolution_url": None,
            "evolution_instance": None
        }

    return {
        "configured": bool(config.evolution_url and config.evolution_key),
        "evolution_url": config.evolution_url,
        "evolution_instance": config.evolution_instance,
        "webhook_url": f"/api/evolution/webhook/{pedido_id}",
        "numeros_atendentes": config.numeros_atendentes
    }


# ============ TESTES ============

@router.post("/test/{pedido_id}")
async def test_evolution_connection(pedido_id: int, db: Session = Depends(get_db)):
    """Testa conexão com Evolution API"""

    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_url or not config.evolution_key:
        raise HTTPException(status_code=400, detail="Evolution não configurado")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{config.evolution_url}/instance/fetchInstances",
                headers={"apikey": config.evolution_key}
            )

            if response.status_code == 200:
                instances = response.json()
                return {
                    "status": "success",
                    "message": "Conexão estabelecida com sucesso!",
                    "instances": instances
                }
            else:
                return {
                    "status": "error",
                    "message": f"Erro na conexão: {response.status_code}"
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar: {str(e)}")


@router.post("/send-test/{pedido_id}")
async def send_test_message(
    pedido_id: int,
    phone: str,
    message: str,
    db: Session = Depends(get_db)
):
    """Envia mensagem de teste"""

    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config or not config.evolution_url or not config.evolution_key:
        raise HTTPException(status_code=400, detail="Evolution não configurado")

    success = await send_whatsapp_message(
        evolution_url=config.evolution_url,
        evolution_key=config.evolution_key,
        instance_name=config.evolution_instance,
        phone=phone,
        message=message
    )

    if success:
        return {"status": "success", "message": "Mensagem enviada com sucesso!"}
    else:
        raise HTTPException(status_code=500, detail="Erro ao enviar mensagem")


# ============ GERENCIAMENTO DE INSTÂNCIAS ============

@router.get("/instance/qrcode/{pedido_id}")
async def obter_qrcode(pedido_id: int, db: Session = Depends(get_db)):
    """
    Obtém o QR Code para conectar o WhatsApp da instância do cliente.
    """
    # Buscar configuração do bot
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    if not config.evolution_instance:
        raise HTTPException(
            status_code=400,
            detail="Instância Evolution API não configurada para este pedido"
        )

    # Obter QR Code via Evolution API
    import evolution_helper
    qrcode_data = evolution_helper.obter_qrcode_instancia(
        config.evolution_url,
        config.evolution_key,
        config.evolution_instance
    )

    if qrcode_data:
        return {
            "success": True,
            "instance_name": config.evolution_instance,
            "qrcode": qrcode_data.get("qrcode"),
            "base64": qrcode_data.get("base64")
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível obter o QR Code. Verifique se a instância está ativa."
        )


@router.get("/instance/status/{pedido_id}")
async def verificar_status(pedido_id: int, db: Session = Depends(get_db)):
    """
    Verifica o status de conexão da instância Evolution API do cliente.
    """
    # Buscar configuração do bot
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    if not config.evolution_instance:
        raise HTTPException(
            status_code=400,
            detail="Instância Evolution API não configurada para este pedido"
        )

    # Verificar status via Evolution API
    import evolution_helper
    status_data = evolution_helper.verificar_status_instancia(
        config.evolution_url,
        config.evolution_key,
        config.evolution_instance
    )

    if status_data:
        return {
            "success": True,
            "instance_name": config.evolution_instance,
            "status": status_data
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível verificar o status da instância"
        )


@router.post("/instance/recreate/{pedido_id}")
async def recriar_instancia(pedido_id: int, db: Session = Depends(get_db)):
    """
    Recria a instância Evolution API para o cliente.
    Útil quando há problemas com a instância atual.
    """
    # Buscar pedido e cliente
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Buscar configuração
    config = db.query(models.ConfiguracaoBot).filter(
        models.ConfiguracaoBot.pedido_id == pedido_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")

    # Deletar instância antiga se existir
    if config.evolution_instance:
        import evolution_helper
        evolution_helper.deletar_instancia(
            config.evolution_url,
            config.evolution_key,
            config.evolution_instance
        )

    # Criar nova instância
    import asyncio
    import evolution_helper
    evolution_result = asyncio.run(
        evolution_helper.criar_instancia_evolution(db, pedido.cliente, pedido)
    )

    if evolution_result and evolution_result.get("success"):
        return {
            "success": True,
            "message": "Instância recriada com sucesso",
            "instance_name": evolution_result.get("instance_name"),
            "qrcode_available": evolution_result.get("qrcode") is not None
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao recriar instância: {evolution_result.get('error') if evolution_result else 'Erro desconhecido'}"
        )
