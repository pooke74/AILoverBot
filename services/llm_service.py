import aiohttp
import logging
from config import OPENROUTER_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, LLM_MODEL, LLM_FALLBACK_MODELS
from prompts.character import get_system_prompt

logger = logging.getLogger(__name__)

async def _call_gemini(messages: list) -> str:
    """Google Gemini API ile cevap al (BIRINCIL - ucretsiz)."""
    if not GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # Gemini formatina cevir
    gemini_contents = []
    system_text = ""
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        elif msg["role"] == "user":
            gemini_contents.append({"role": "user", "parts": [{"text": msg["content"]}]})
        elif msg["role"] == "assistant":
            gemini_contents.append({"role": "model", "parts": [{"text": msg["content"]}]})
    
    payload = {
        "contents": gemini_contents,
        "systemInstruction": {"parts": [{"text": system_text}]} if system_text else None,
        "generationConfig": {
            "temperature": 0.85,
            "maxOutputTokens": 300
        }
    }
    # None olan key'leri kaldir
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    logger.info("LLM basarili: model=gemini-2.0-flash (Google)")
                    return content
                else:
                    error_text = await response.text()
                    logger.warning(f"Gemini hata: status={response.status}, error={error_text[:200]}")
                    return None
    except Exception as e:
        logger.error(f"Gemini baglanti hatasi: {e}")
        return None

async def _call_openai(messages: list) -> str:
    """OpenAI API (GPT-4o-mini) ile cevap al."""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        return None
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
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
                    logger.warning(f"OpenAI hata: status={response.status}")
                    return None
    except Exception as e:
        logger.error(f"OpenAI baglanti hatasi: {e}")
        return None

async def _call_openrouter(model: str, messages: list) -> str:
    """OpenRouter API ile cevap al."""
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        return None
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost", 
        "X-Title": "AILoverBot"
    }
    payload = {
        "model": model,
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
                    logger.warning(f"OpenRouter hata: model={model}, status={response.status}")
                    return None
    except Exception as e:
        logger.error(f"OpenRouter baglanti hatasi: {e}")
        return None

async def generate_response(chat_history: list, character_id: str = 'mia') -> str:
    """
    Oncelik sirasi: 1) Gemini (ucretsiz)  2) OpenAI  3) OpenRouter
    """
    system_prompt = get_system_prompt(character_id)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history)
    
    # 1. Gemini dene (birincil, ucretsiz)
    result = await _call_gemini(messages)
    if result:
        return result
    
    # 2. OpenAI dene
    result = await _call_openai(messages)
    if result:
        return result
    
    # 3. OpenRouter modellerini dene
    all_models = [LLM_MODEL] + LLM_FALLBACK_MODELS
    for model in all_models:
        result = await _call_openrouter(model, messages)
        if result:
            return result
    
    logger.error("Tum LLM servisleri basarisiz oldu!")
    return "Simdi biraz mesgulum, birazdan tekrar yaz bana..."
