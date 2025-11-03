"""
Serviço de Áudio
- Transcrição de áudio usando Whisper
- Geração de áudio (TTS) usando gTTS
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
import whisper
from gtts import gTTS
from pydub import AudioSegment
import requests


class AudioService:
    def __init__(self, whisper_model: str = "base", audio_cache_dir: str = "storage/audio_cache"):
        """
        Inicializa serviço de áudio

        Args:
            whisper_model: Modelo do Whisper (tiny, base, small, medium, large)
            audio_cache_dir: Diretório para cache de áudios
        """
        self.whisper_model_name = whisper_model
        self.whisper_model = None  # Lazy loading
        self.audio_cache_dir = Path(audio_cache_dir)
        self.audio_cache_dir.mkdir(parents=True, exist_ok=True)

    def _load_whisper_model(self):
        """Carrega modelo Whisper (lazy loading)"""
        if self.whisper_model is None:
            print(f"🎙️  Carregando modelo Whisper: {self.whisper_model_name}")
            self.whisper_model = whisper.load_model(self.whisper_model_name)
            print("✅ Modelo Whisper carregado")

    def transcribe_audio(self, audio_path: str, language: str = "pt") -> str:
        """
        Transcreve áudio para texto usando Whisper

        Args:
            audio_path: Caminho do arquivo de áudio
            language: Idioma do áudio (pt, en, es, etc)

        Returns:
            Texto transcrito
        """
        try:
            self._load_whisper_model()

            print(f"🎙️  Transcrevendo áudio: {audio_path}")

            # Transcrever
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                fp16=False  # Compatibilidade com CPU
            )

            transcription = result["text"].strip()
            print(f"✅ Transcrição: {transcription}")

            return transcription

        except Exception as e:
            print(f"❌ Erro ao transcrever áudio: {e}")
            raise

    def download_audio_from_url(self, url: str, save_path: Optional[str] = None) -> str:
        """
        Baixa áudio de uma URL

        Args:
            url: URL do áudio
            save_path: Caminho onde salvar (opcional)

        Returns:
            Caminho do arquivo baixado
        """
        try:
            print(f"⬇️  Baixando áudio: {url}")

            # Criar caminho temporário se não fornecido
            if save_path is None:
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
                save_path = temp_file.name
                temp_file.close()

            # Baixar áudio
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Salvar
            with open(save_path, 'wb') as f:
                f.write(response.content)

            print(f"✅ Áudio baixado: {save_path}")
            return save_path

        except Exception as e:
            print(f"❌ Erro ao baixar áudio: {e}")
            raise

    def convert_audio_format(self, input_path: str, output_format: str = "wav") -> str:
        """
        Converte áudio para outro formato

        Args:
            input_path: Caminho do áudio de entrada
            output_format: Formato de saída (wav, mp3, ogg)

        Returns:
            Caminho do arquivo convertido
        """
        try:
            print(f"🔄 Convertendo áudio para {output_format}")

            # Carregar áudio
            audio = AudioSegment.from_file(input_path)

            # Criar caminho de saída
            output_path = str(Path(input_path).with_suffix(f".{output_format}"))

            # Exportar
            audio.export(output_path, format=output_format)

            print(f"✅ Áudio convertido: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Erro ao converter áudio: {e}")
            raise

    def text_to_speech(self, text: str, output_path: Optional[str] = None, language: str = "pt-br") -> str:
        """
        Converte texto em áudio usando gTTS

        Args:
            text: Texto para converter
            output_path: Caminho onde salvar (opcional)
            language: Idioma (pt-br, en, es, etc)

        Returns:
            Caminho do arquivo de áudio gerado
        """
        try:
            print(f"🔊 Gerando áudio: {text[:50]}...")

            # Criar caminho se não fornecido
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp3",
                    dir=self.audio_cache_dir
                )
                output_path = temp_file.name
                temp_file.close()

            # Gerar áudio
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(output_path)

            print(f"✅ Áudio gerado: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Erro ao gerar áudio: {e}")
            raise

    def process_whatsapp_audio(self, audio_url: str) -> str:
        """
        Pipeline completo para processar áudio do WhatsApp
        1. Baixa o áudio
        2. Converte para WAV
        3. Transcreve

        Args:
            audio_url: URL do áudio do WhatsApp

        Returns:
            Texto transcrito
        """
        temp_files = []

        try:
            # Baixar áudio
            audio_path = self.download_audio_from_url(audio_url)
            temp_files.append(audio_path)

            # Converter para WAV (Whisper funciona melhor com WAV)
            wav_path = self.convert_audio_format(audio_path, "wav")
            temp_files.append(wav_path)

            # Transcrever
            transcription = self.transcribe_audio(wav_path, language="pt")

            return transcription

        finally:
            # Limpar arquivos temporários
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    print(f"⚠️  Erro ao remover arquivo temporário {temp_file}: {e}")

    def generate_response_audio(self, text: str, phone_number: str) -> str:
        """
        Gera áudio de resposta para o WhatsApp

        Args:
            text: Texto da resposta
            phone_number: Número do telefone (para organizar cache)

        Returns:
            Caminho do arquivo de áudio
        """
        # Criar diretório específico do número
        phone_cache_dir = self.audio_cache_dir / phone_number
        phone_cache_dir.mkdir(parents=True, exist_ok=True)

        # Gerar nome do arquivo baseado no hash do texto
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()[:10]
        audio_filename = f"response_{text_hash}.mp3"
        audio_path = phone_cache_dir / audio_filename

        # Se já existe em cache, retornar
        if audio_path.exists():
            print(f"📦 Áudio encontrado em cache: {audio_path}")
            return str(audio_path)

        # Gerar áudio
        return self.text_to_speech(text, str(audio_path))

    def cleanup_cache(self, phone_number: Optional[str] = None, max_age_days: int = 7):
        """
        Limpa cache de áudios antigos

        Args:
            phone_number: Número específico para limpar (opcional)
            max_age_days: Idade máxima dos arquivos em dias
        """
        import time
        from datetime import datetime, timedelta

        try:
            # Definir diretório
            if phone_number:
                cache_dir = self.audio_cache_dir / phone_number
            else:
                cache_dir = self.audio_cache_dir

            if not cache_dir.exists():
                return

            # Calcular timestamp de corte
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)

            # Remover arquivos antigos
            removed_count = 0
            for audio_file in cache_dir.rglob("*.mp3"):
                if audio_file.stat().st_mtime < cutoff_time:
                    audio_file.unlink()
                    removed_count += 1

            if removed_count > 0:
                print(f"🗑️  Removidos {removed_count} áudios antigos do cache")

        except Exception as e:
            print(f"⚠️  Erro ao limpar cache: {e}")
