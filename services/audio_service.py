import aiohttp
import os
import uuid
from config import ELEVENLABS_API_KEY

# Rachel voice ID (ElevenLabs Default)
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

async def generate_audio(text: str) -> str:
    """
    ElevenLabs API üzerinden metni sese dönüştürür ve kaydedilen dosyasının yolunu döner.
    """
    if not ELEVENLABS_API_KEY or ELEVENLABS_API_KEY == "your_elevenlabs_api_key_here":
        print("ELEVENLABS_API_KEY eksik.")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    audio_content = await response.read()
                    
                    # Dosyayı kaydetmek için temp dizini oluştur
                    os.makedirs("temp_audio", exist_ok=True)
                    filename = f"temp_audio/{uuid.uuid4()}.ogg"
                    
                    with open(filename, "wb") as f:
                        f.write(audio_content)
                    return filename
                else:
                    error_text = await response.text()
                    print(f"ElevenLabs Error: {response.status} - {error_text}")
                    return None
    except Exception as e:
        print(f"Ses API Hatası: {e}")
        return None
