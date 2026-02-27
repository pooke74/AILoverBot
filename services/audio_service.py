import aiohttp
import os
import uuid
import logging
from config import ELEVENLABS_API_KEY

logger = logging.getLogger(__name__)

# Her karakter icin farkli ElevenLabs ses ID'leri
# https://elevenlabs.io/app/voice-library adresinden secildi
CHARACTER_VOICES = {
    "mia": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Rachel - sicak, samimi
        "stability": 0.5,
        "similarity_boost": 0.75,
    },
    "elif": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel -> deeper tone
        "stability": 0.4,
        "similarity_boost": 0.8,
    },
    "yuki": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Domi - genc, tatli
        "stability": 0.6,
        "similarity_boost": 0.7,
    },
    "defne": {
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",  # Elli - sik, modern
        "stability": 0.45,
        "similarity_boost": 0.8,
    }
}

DEFAULT_VOICE = "EXAVITQu4vr4xnSDxMaL"  # Rachel

async def generate_audio(text: str, character_id: str = 'mia') -> str:
    """
    ElevenLabs API ile metni sese donusturur. Karakter bazli ses kullanir.
    """
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your_elevenlabs_api_key_here":
        logger.warning("ELEVENLABS_API_KEY eksik.")
        return None

    # Karakter bazli ses ayarlari
    voice_config = CHARACTER_VOICES.get(character_id, CHARACTER_VOICES.get("mia"))
    voice_id = voice_config["voice_id"]
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    # Cok uzun metinleri kes (ElevenLabs limiti)
    if len(text) > 500:
        text = text[:497] + "..."
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": voice_config.get("stability", 0.5),
            "similarity_boost": voice_config.get("similarity_boost", 0.75)
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    audio_content = await response.read()
                    os.makedirs("temp_audio", exist_ok=True)
                    filename = f"temp_audio/{uuid.uuid4()}.ogg"
                    with open(filename, "wb") as f:
                        f.write(audio_content)
                    logger.info(f"Ses basarili: karakter={character_id}, voice={voice_id}")
                    return filename
                else:
                    error_text = await response.text()
                    logger.warning(f"ElevenLabs hata: {response.status} - {error_text[:150]}")
                    return None
    except Exception as e:
        logger.error(f"Ses API hatasi: {e}")
        return None
