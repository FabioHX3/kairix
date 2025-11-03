"""
Handler de mensagens para Agente IA
Processa mensagens do WhatsApp usando RAG + Áudio
"""
import os
from typing import Dict, Optional
import httpx
from pathlib import Path

from services.rag_service import RAGService
from services.audio_service import AudioService
from config_helper import get_qdrant_url, get_ollama_url, get_ollama_model, get_ollama_embeddings_model, get_evolution_api_url, get_evolution_api_key


class IAHandler:
    def __init__(self):
        """Inicializa handler de IA"""
        # Configurações
        self.qdrant_url = get_qdrant_url()
        self.ollama_url = get_ollama_url()
        self.embeddings_model = get_ollama_embeddings_model()
        self.llm_model = get_ollama_model()
        self.evolution_url = get_evolution_api_url()
        self.evolution_api_key = get_evolution_api_key()

        # Serviços
        self.rag_service = RAGService(
            qdrant_url=self.qdrant_url,
            ollama_url=self.ollama_url,
            embeddings_model=self.embeddings_model,
            llm_model=self.llm_model
        )
        self.audio_service = AudioService(whisper_model="base")

    async def send_message(self, instance_name: str, phone_number: str, text: str) -> bool:
        """
        Envia mensagem de texto via Evolution API

        Args:
            instance_name: Nome da instância do Evolution
            phone_number: Número do destinatário
            text: Texto da mensagem

        Returns:
            True se enviado com sucesso
        """
        try:
            url = f"{self.evolution_url}/message/sendText/{instance_name}"

            payload = {
                "number": phone_number,
                "text": text
            }

            headers = {
                "apikey": self.evolution_api_key,
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

            print(f"✅ Mensagem enviada para {phone_number}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar mensagem: {e}")
            return False

    async def send_audio(self, instance_name: str, phone_number: str, audio_path: str) -> bool:
        """
        Envia mensagem de áudio via Evolution API

        Args:
            instance_name: Nome da instância
            phone_number: Número do destinatário
            audio_path: Caminho do arquivo de áudio

        Returns:
            True se enviado com sucesso
        """
        try:
            url = f"{self.evolution_url}/message/sendMedia/{instance_name}"

            # Ler áudio como base64
            import base64
            with open(audio_path, 'rb') as f:
                audio_base64 = base64.b64encode(f.read()).decode()

            payload = {
                "number": phone_number,
                "mediatype": "audio",
                "mimetype": "audio/mpeg",
                "media": audio_base64,
                "fileName": Path(audio_path).name
            }

            headers = {
                "apikey": self.evolution_api_key,
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

            print(f"🔊 Áudio enviado para {phone_number}")
            return True

        except Exception as e:
            print(f"❌ Erro ao enviar áudio: {e}")
            return False

    async def send_presence(self, instance_name: str, phone_number: str, state: str = "composing") -> bool:
        """
        Envia indicador de presença (digitando...) via Evolution API

        Args:
            instance_name: Nome da instância
            phone_number: Número do destinatário
            state: Estado da presença ("composing" para digitando, "available" para disponível)

        Returns:
            True se enviado com sucesso
        """
        try:
            url = f"{self.evolution_url}/chat/sendPresence/{instance_name}"

            payload = {
                "number": phone_number,
                "presence": state,
                "delay": 3000  # 3 segundos
            }

            headers = {
                "apikey": self.evolution_api_key,
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

            print(f"⌨️  Status '{state}' enviado para {phone_number}")
            return True

        except Exception as e:
            print(f"⚠️ Erro ao enviar status de presença: {e}")
            return False

    async def process_text_message(
        self,
        instance_name: str,
        phone_number: str,
        message_text: str,
        config: Dict
    ) -> bool:
        """
        Processa mensagem de texto do usuário

        Args:
            instance_name: Nome da instância Evolution
            phone_number: Número do remetente (sem máscaras)
            message_text: Texto da mensagem
            config: Configurações do bot

        Returns:
            True se processado com sucesso
        """
        try:
            print(f"💬 Processando mensagem de texto: {message_text}")

            # DESABILITADO: send_presence trava o processamento
            # try:
            #     await self.send_presence(instance_name, phone_number, "composing")
            # except Exception as e:
            #     print(f"⚠️ Erro ao enviar presença (continuando...): {e}")

            # Verificar se é comando de atendente
            if self._is_attendant_request(message_text):
                return await self._transfer_to_attendant(instance_name, phone_number, config)

            # Verificar se é saudação simples (resposta rápida sem RAG)
            if self._is_greeting(message_text):
                greeting_response = "Olá! 👋 Como posso ajudar você hoje?\n\nPode fazer suas perguntas que responderei com base nas informações disponíveis.\n\n_Para falar com um atendente humano, digite *atendente*._"
                await self.send_message(instance_name, phone_number, greeting_response)
                print(f"✅ Resposta rápida de saudação enviada!")
                return True

            # Processar pergunta com RAG (usando instance_name como identificador da coleção)
            print(f"🔍 Iniciando processamento RAG para: {message_text[:50]}...")

            # Executar RAG de forma assíncrona para não bloquear
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            try:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    # Adicionar timeout de 120 segundos (Ollama precisa mais tempo)
                    answer = await asyncio.wait_for(
                        loop.run_in_executor(
                            executor,
                            self.rag_service.process_question,
                            instance_name,
                            message_text
                        ),
                        timeout=120.0
                    )
                print(f"✅ RAG completou! Resposta: {answer[:100]}...")
            except asyncio.TimeoutError:
                print(f"⏱️ Timeout no processamento RAG (120s)")
                answer = "⚠️ Sistema de IA não disponível no momento.\n\nPor favor:\n• Digite *atendente* para falar com um humano\n• Ou aguarde alguns instantes e tente novamente"
            except Exception as e:
                print(f"❌ Erro no processamento RAG: {e}")
                import traceback
                traceback.print_exc()

                # Resposta de fallback se RAG falhar
                answer = "⚠️ Sistema de IA não disponível no momento.\n\nPor favor:\n• Digite *atendente* para falar com um humano\n• Ou aguarde alguns instantes e tente novamente"

            # Enviar resposta em texto
            print(f"📤 Enviando resposta para {phone_number}...")
            await self.send_message(instance_name, phone_number, answer)
            print(f"✅ Resposta enviada com sucesso!")

            # Gerar e enviar áudio da resposta (DESABILITADO - apenas texto)
            # audio_path = self.audio_service.generate_response_audio(answer, phone_number)
            # await self.send_audio(instance_name, phone_number, audio_path)

            return True

        except Exception as e:
            print(f"❌ Erro ao processar mensagem de texto: {e}")

            # Enviar mensagem de erro
            error_msg = "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente ou digite *atendente* para falar com um humano."
            await self.send_message(instance_name, phone_number, error_msg)

            return False

    async def process_audio_message(
        self,
        instance_name: str,
        phone_number: str,
        audio_url: str,
        config: Dict
    ) -> bool:
        """
        Processa mensagem de áudio do usuário

        Args:
            instance_name: Nome da instância Evolution
            phone_number: Número do remetente
            audio_url: URL do áudio
            config: Configurações do bot

        Returns:
            True se processado com sucesso
        """
        try:
            print(f"🎙️  Processando mensagem de áudio de {phone_number}")

            # DESABILITADO: send_presence trava o processamento
            # try:
            #     await self.send_presence(instance_name, phone_number, "composing")
            # except Exception as e:
            #     print(f"⚠️ Erro ao enviar presença (continuando...): {e}")

            # Transcrever áudio
            transcription = self.audio_service.process_whatsapp_audio(audio_url)
            print(f"📝 Transcrição: {transcription}")

            # Verificar se é comando de atendente
            if self._is_attendant_request(transcription):
                return await self._transfer_to_attendant(instance_name, phone_number, config)

            # Processar pergunta com RAG (usando instance_name como identificador da coleção)
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            try:
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as executor:
                    answer = await loop.run_in_executor(
                        executor,
                        self.rag_service.process_question,
                        instance_name,
                        transcription
                    )
            except Exception as e:
                print(f"❌ Erro no processamento RAG de áudio: {e}")
                import traceback
                traceback.print_exc()

                answer = "Desculpe, tive um problema ao processar seu áudio. Por favor, tente novamente ou digite *atendente* para falar com um humano."

            # Enviar resposta em texto
            await self.send_message(instance_name, phone_number, f"🎙️ *Você disse:* {transcription}\n\n{answer}")

            # Gerar e enviar áudio da resposta (DESABILITADO - apenas texto)
            # audio_path = self.audio_service.generate_response_audio(answer, phone_number)
            # await self.send_audio(instance_name, phone_number, audio_path)

            return True

        except Exception as e:
            print(f"❌ Erro ao processar áudio: {e}")

            error_msg = "Desculpe, não consegui processar seu áudio. Por favor, envie uma mensagem de texto ou digite *atendente*."
            await self.send_message(instance_name, phone_number, error_msg)

            return False

    def _is_attendant_request(self, text: str) -> bool:
        """
        Verifica se a mensagem é um pedido para falar com atendente

        Args:
            text: Texto da mensagem

        Returns:
            True se for pedido de atendente
        """
        keywords = [
            "atendente",
            "atendimento",
            "humano",
            "pessoa",
            "operador",
            "falar com alguem",
            "falar com alguém",
            "atender"
        ]

        text_lower = text.lower().strip()

        return any(keyword in text_lower for keyword in keywords)

    def _is_greeting(self, text: str) -> bool:
        """
        Verifica se a mensagem é uma saudação simples

        Args:
            text: Texto da mensagem

        Returns:
            True se for saudação
        """
        greetings = [
            "oi", "olá", "ola", "hey", "opa", "eae", "e ai", "eai",
            "bom dia", "boa tarde", "boa noite",
            "tudo bem", "tudo bom", "como vai",
            "alo", "alô"
        ]

        text_lower = text.lower().strip()

        # Verificar se é saudação exata ou começa com saudação
        return text_lower in greetings or any(text_lower.startswith(g) for g in greetings)

    async def _transfer_to_attendant(
        self,
        instance_name: str,
        phone_number: str,
        config: Dict
    ) -> bool:
        """
        Transfere conversa para atendente humano

        Args:
            instance_name: Nome da instância
            phone_number: Número do cliente
            config: Configurações do bot

        Returns:
            True se transferido com sucesso
        """
        try:
            print(f"👤 Transferindo {phone_number} para atendente")

            # Verificar se há números de atendentes configurados
            numeros_atendentes = config.get("numeros_atendentes", [])

            if not numeros_atendentes:
                msg = "⚠️ No momento não há atendentes disponíveis. Por favor, tente novamente mais tarde ou envie um email para contato@empresa.com"
                await self.send_message(instance_name, phone_number, msg)
                return False

            # Mensagem para o cliente
            msg_cliente = "✅ Você está sendo transferido para um atendente humano. Aguarde um momento..."
            await self.send_message(instance_name, phone_number, msg_cliente)

            # Notificar atendentes
            for atendente_number in numeros_atendentes:
                msg_atendente = f"🔔 *Novo atendimento*\n\nCliente: {phone_number}\nSolicitou atendimento humano.\n\nResponda diretamente para o número do cliente."
                await self.send_message(instance_name, atendente_number, msg_atendente)

            return True

        except Exception as e:
            print(f"❌ Erro ao transferir para atendente: {e}")
            return False

    async def send_welcome_message(self, instance_name: str, phone_number: str) -> bool:
        """
        Envia mensagem de boas-vindas para novo contato

        Args:
            instance_name: Nome da instância
            phone_number: Número do cliente

        Returns:
            True se enviado com sucesso
        """
        welcome_text = """👋 Olá! Seja bem-vindo!

Sou o assistente inteligente e estou aqui para ajudar você com suas dúvidas.

Você pode:
✅ Enviar suas perguntas por *texto*
✅ Enviar suas perguntas por *áudio*

Respondo das duas formas para sua comodidade!

📌 Para falar com um atendente humano, digite *atendente* a qualquer momento.

Como posso ajudar você hoje?"""

        return await self.send_message(instance_name, phone_number, welcome_text)

    async def handle_message(
        self,
        instance_name: str,
        message_data: Dict,
        config: Dict
    ) -> bool:
        """
        Handler principal de mensagens

        Args:
            instance_name: Nome da instância Evolution
            message_data: Dados da mensagem do webhook
            config: Configurações do bot

        Returns:
            True se processado com sucesso
        """
        try:
            # Extrair informações da mensagem
            message = message_data.get("message", {})
            key = message_data.get("key", {})

            # Número do remetente
            from_number = key.get("remoteJid", "").replace("@s.whatsapp.net", "")

            # Ignorar mensagens do próprio bot
            if key.get("fromMe", False):
                return True

            # Limpar número (somente dígitos)
            phone_number = ''.join(filter(str.isdigit, from_number))

            print(f"📱 Mensagem recebida de: {phone_number}")

            # Verificar tipo de mensagem (está no nível raiz de message_data)
            message_type = message_data.get("messageType", "")

            if message_type == "conversation" or message_type == "extendedTextMessage":
                # Mensagem de texto
                text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text", "")

                return await self.process_text_message(
                    instance_name,
                    phone_number,
                    text,
                    config
                )

            elif message_type == "audioMessage":
                # Mensagem de áudio
                audio_message = message.get("audioMessage", {})
                audio_url = audio_message.get("url", "")

                if not audio_url:
                    print("⚠️ URL do áudio não encontrada")
                    return False

                return await self.process_audio_message(
                    instance_name,
                    phone_number,
                    audio_url,
                    config
                )

            else:
                # Tipo de mensagem não suportado
                print(f"⚠️ Tipo de mensagem não suportado: {message_type}")

                msg = "Desculpe, só consigo processar mensagens de *texto* e *áudio*. Por favor, envie sua mensagem nesses formatos."
                await self.send_message(instance_name, phone_number, msg)

                return False

        except Exception as e:
            print(f"❌ Erro no handler de mensagem: {e}")
            import traceback
            traceback.print_exc()
            return False
