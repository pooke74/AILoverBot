import aiohttp
import logging
import urllib.parse
from config import FAL_API_KEY
from prompts.character import get_image_base_prompt

logger = logging.getLogger(__name__)

async def generate_image(prompt: str, character_id: str = 'mia') -> str:
    """
    Gorsel uretir. Oncelik: 1) Fal.ai  2) Pollinations.ai (ucretsiz, key gerekmez)
    """
    # Karaktere ozel sabit yuz promptu
    base_prompt = get_image_base_prompt(character_id)
    full_prompt = base_prompt + prompt
    
    # 1. Fal.ai dene (bakiye varsa)
    if FAL_API_KEY and FAL_API_KEY != "your_fal_api_key_here":
        result = await _call_fal(full_prompt)
        if result:
            return result
    
    # 2. Pollinations.ai (ucretsiz fallback)
    result = await _call_pollinations(full_prompt)
    if result:
        return result
    
    logger.error("Tum gorsel servisleri basarisiz!")
    return None

async def _call_fal(full_prompt: str) -> str:
    """Fal.ai Flux LoRA ile gorsel uret."""
    negative_prompt = "multiple people, deformed face, ugly, blurry, low quality, cartoon, anime, drawing, text, watermark"
    
    url = "https://fal.run/fal-ai/flux-lora"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "image_size": "portrait_4_3",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "seed": 42
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Gorsel basarili: Fal.ai")
                    return data['images'][0]['url']
                else:
                    error_text = await response.text()
                    logger.warning(f"Fal.ai hata: {response.status} - {error_text[:150]}")
                    return None
    except Exception as e:
        logger.error(f"Fal.ai baglanti hatasi: {e}")
        return None

async def _call_pollinations(full_prompt: str) -> str:
    """Pollinations.ai ile ucretsiz gorsel uret (API key gerekmez)."""
    try:
        encoded_prompt = urllib.parse.quote(full_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&seed=42&model=flux&nologo=true"
        
        # URL'nin calistigini dogrula
        async with aiohttp.ClientSession() as session:
            async with session.head(image_url, allow_redirects=True) as response:
                if response.status == 200:
                    logger.info("Gorsel basarili: Pollinations.ai")
                    return image_url
                else:
                    logger.warning(f"Pollinations.ai hata: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Pollinations.ai baglanti hatasi: {e}")
        return None
