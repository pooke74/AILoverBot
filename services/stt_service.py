import aiohttp
import os
import uuid
from config import OPENAI_API_KEY

async def transcribe_voice(file_path: str) -> str:
    """
    OpenAI Whisper API kullanarak ses dosyasını metne çevirir.
    Kullanıcının sesli mesajını anlamamızı sağlar.
    """
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("OPENAI_API_KEY eksik (Whisper STT için gerekli).")
        return None
    
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
    
    try:
        import aiohttp
        data = aiohttp.FormData()
        data.add_field('file', open(file_path, 'rb'), filename='voice.ogg', content_type='audio/ogg')
        data.add_field('model', 'whisper-1')
        data.add_field('language', 'tr')  # Türkçe öncelikli
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('text', '')
                else:
                    error_text = await response.text()
                    print(f"Whisper Error: {response.status} - {error_text}")
                    return None
    except Exception as e:
        print(f"Whisper STT Hatası: {e}")
        return None
    finally:
        # Geçici dosyayı temizle
        if os.path.exists(file_path):
            os.remove(file_path)
