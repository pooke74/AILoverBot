import aiohttp
import json
from config import OPENROUTER_API_KEY, LLM_MODEL
from prompts.character import get_system_prompt

async def generate_response(chat_history: list, character_id: str = 'mia') -> str:
    """
    chat_history: [{"role": "user"|"assistant", "content": "mesaj"}, ...] formatında olmalı.
    character_id: Aktif karakter ID'si (mia, elif, yuki, defne).
    """
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        return "Şu an bağlantımda bir sorun var tatlım... (OpenRouter API Key eksik)"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost", 
        "X-Title": "AILoverBot"
    }
    
    # Seçilen karaktere göre system prompt al
    system_prompt = get_system_prompt(character_id)
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    messages.extend(chat_history)
    
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.85,
        "max_tokens": 300
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    print(f"OpenRouter Error: {response.status} - {error_text}")
                    return "Bunu tam anlayamadım, tekrar söyler misin? 😅"
    except Exception as e:
        print(f"LLM API Hatası: {e}")
        return "Şu an kafam biraz karışık, sonra tekrar yazsana... 😞"
