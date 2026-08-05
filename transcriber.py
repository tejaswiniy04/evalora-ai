"""
transcriber.py — Multilingual Speech-to-Text Engine using Groq Whisper
========================================================================
Transcribes recorded audio bytes into text using Groq's whisper-large-v3 model.
Supports 99+ global languages with automatic language detection and manual language selection.
"""

import io
import logging
import os
import time

logger = logging.getLogger(__name__)

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3")

# Map of user-friendly display names to ISO-639-1 language codes
SUPPORTED_LANGUAGES = {
    "🌐 Auto-Detect (99+ Languages)": None,
    "🇮🇳 Hindi (हिन्दी)": "hi",
    "🇮🇳 Kannada (ಕನ್ನಡ)": "kn",
    "🇮🇳 Telugu (తెలుగు)": "te",
    "🇮🇳 Tamil (தமிழ்)": "ta",
    "🇮🇳 Bengali (বাংলা)": "bn",
    "🇮🇳 Marathi (मराठी)": "mr",
    "🇮🇳 Gujarati (ગુજરાતી)": "gu",
    "🇮🇳 Malayalam (മലയാളം)": "ml",
    "🇮🇳 Punjabi (ਪੰਜਾਬੀ)": "pa",
    "🇬🇧 English": "en",
    "🇪🇸 Spanish (Español)": "es",
    "🇫🇷 French (Français)": "fr",
    "🇩🇪 German (Deutsch)": "de",
    "🇯🇵 Japanese (日本語)": "ja",
    "🇨🇳 Chinese (中文)": "zh",
    "🇦🇪 Arabic (العربية)": "ar",
    "🇷🇺 Russian (Русский)": "ru",
    "🇵🇹 Portuguese (Português)": "pt",
    "🇰🇷 Korean (한국어)": "ko",
}


def transcribe_audio(audio_bytes: bytes, client, filename: str = "recording.wav", language: str = None) -> str:
    """
    Transcribe raw audio bytes using Groq Whisper API (whisper-large-v3).

    Args:
        audio_bytes: Raw bytes of the recorded audio file.
        client:      Initialized Groq client instance.
        filename:    Virtual filename with extension (e.g. 'recording.wav').
        language:    ISO-639-1 language code (e.g. 'hi', 'kn', 'te', 'ta', 'en', 'es').
                     If None or 'auto', Whisper auto-detects language across 99+ languages.

    Returns:
        Transcribed text string.
    """
    if not audio_bytes:
        return ""

    # Create a named buffer for the Groq client
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename

    max_retries = 3
    for attempt in range(max_retries):
        try:
            kwargs = {
                "file": audio_file,
                "model": WHISPER_MODEL,
                "prompt": "The candidate is answering a professional job interview question.",
                "response_format": "text",
                "temperature": 0.0,
            }
            if language and language != "auto":
                kwargs["language"] = language

            transcription = client.audio.transcriptions.create(**kwargs)

            # Groq returns plain text when response_format="text", or dict/object when json
            if isinstance(transcription, str):
                text = transcription.strip()
            else:
                text = getattr(transcription, "text", str(transcription)).strip()

            logger.info(f"Audio transcribed successfully ({len(text)} chars, language='{language or 'auto'}')")
            return text

        except Exception as e:
            logger.warning(f"Whisper API attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Speech-to-Text transcription failed: {e}") from e
            time.sleep(1)

    return ""
