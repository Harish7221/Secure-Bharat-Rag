import os
import requests
from dotenv import load_dotenv

load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

def translate_document_to_english(text: str) -> str:
    """
    Translates full document text to English.
    Handles large text by batching.
    """

    MAX_CHARS = 4000  # adjust based on Sarvam limits

    translated_parts = []

    for i in range(0, len(text), MAX_CHARS):
        chunk = text[i:i+MAX_CHARS]
        translated = sarvam_translate_to_english(chunk)
        translated_parts.append(translated)

    return "\n".join(translated_parts)

def sarvam_speech_to_text(audio_path: str):
    url = "https://api.sarvam.ai/speech-to-text"  # example endpoint

    with open(audio_path, "rb") as f:
        files = {"file": f}
        headers = {"Authorization": f"Bearer {SARVAM_API_KEY}"}

        response = requests.post(url, files=files, headers=headers)

    return response.json().get("text", "")


def sarvam_translate_to_english(text: str):
    url = "https://api.sarvam.ai/translate"

    headers = {
        "Authorization": f"Bearer {SARVAM_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "source_language": "auto",
        "target_language": "en",
        "text": text
    }

    response = requests.post(url, json=data, headers=headers)

    return response.json().get("translated_text", text)

