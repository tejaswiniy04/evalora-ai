"""
transcriber.py — Speech-to-Text Transcription Engine using Groq Whisper
========================================================================
Transcribes recorded audio bytes into text using Groq's whisper-large-v3 model.
"""

import io
import logging
import os
import time

logger = logging.getLogger(__name__)

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3")


def transcribe_audio(audio_bytes: bytes, client, filename: str = "recording.wav") -> str:
    """
    Transcribe raw audio bytes using Groq Whisper API (whisper-large-v3).

    Args:
        audio_bytes: Raw bytes of the recorded audio file.
        client:      Initialized Groq client instance.
        filename:    Virtual filename with extension (e.g. 'recording.wav').

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
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model=WHISPER_MODEL,
                prompt="The candidate is answering a professional job interview question.",
                response_format="text",
                temperature=0.0,
            )

            # Groq returns plain text when response_format="text", or dict/object when json
            if isinstance(transcription, str):
                text = transcription.strip()
            else:
                text = getattr(transcription, "text", str(transcription)).strip()

            logger.info(f"Audio transcribed successfully ({len(text)} chars)")
            return text

        except Exception as e:
            logger.warning(f"Whisper API attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise RuntimeError(f"Speech-to-Text transcription failed: {e}") from e
            time.sleep(1)

    return ""
