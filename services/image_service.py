import aiohttp
import logging
import base64
import os
import uuid
import urllib.parse
from config import FAL_API_KEY, GEMINI_API_KEY
from prompts.character import get_image_base_prompt

logger = logging.getLogger(__name__)

async def generate_image(prompt: str, character_id: str = 'mia', use_raw_prompt: bool = False) -> str:
    """
    Gorsel uretir. Oncelik: 1) Gemini Image Gen  2) Fal.ai  3) Pollinations
    use_raw_prompt=True ise prompt'a base_prompt eklenmez (zaten ekli).
    """
    if use_raw_prompt:
        full_prompt = prompt
    else:
        base_prompt = get_image_base_prompt(character_id)
        full_prompt = base_prompt + prompt
    
    # 1. Gemini Image Generation (ucretsiz, calisiyor!)
    result = await _call_gemini_image(full_prompt)
    if result:
        return result
    
    # 2. Fal.ai (bakiye varsa)
    if FAL_API_KEY and FAL_API_KEY != "your_fal_api_key_here":
        result = await _call_fal(full_prompt)
        if result:
            return result
    
    # 3. Pollinations fallback
    result = await _call_pollinations(full_prompt)
    if result:
        return result
    
    logger.error("Tum gorsel servisleri basarisiz!")
    return None

async def _call_gemini_image(full_prompt: str) -> str:
    """Gemini 2.0 Flash Image Generation ile gorsel uret (UCRETSIZ)."""
    if not GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Generate this image: {full_prompt}"}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    data = await response.json()
                    for cand in data.get('candidates', []):
                        for part in cand.get('content', {}).get('parts', []):
                            if 'inlineData' in part:
                                mime = part['inlineData'].get('mimeType', 'image/png')
                                ext = 'png' if 'png' in mime else 'jpg'
                                img_data = base64.b64decode(part['inlineData']['data'])
                                os.makedirs("temp_images", exist_ok=True)
                                filepath = f"temp_images/{uuid.uuid4()}.{ext}"
                                with open(filepath, 'wb') as f:
                                    f.write(img_data)
                                logger.info(f"Gorsel basarili: Gemini Image Gen ({len(img_data)} bytes)")
                                return filepath
                    logger.warning("Gemini Image: response icinde gorsel bulunamadi")
                    return None
                else:
                    error_text = await response.text()
                    logger.warning(f"Gemini Image hata: {response.status} - {error_text[:150]}")
                    return None
    except Exception as e:
        logger.error(f"Gemini Image baglanti hatasi: {e}")
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
                    logger.warning(f"Fal.ai hata: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Fal.ai baglanti hatasi: {e}")
        return None

async def _call_pollinations(full_prompt: str) -> str:
    """Pollinations.ai ile ucretsiz gorsel uret."""
    try:
        encoded_prompt = urllib.parse.quote(full_prompt[:500])
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=1024&seed=42&nologo=true"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    os.makedirs("temp_images", exist_ok=True)
                    filepath = f"temp_images/{uuid.uuid4()}.jpg"
                    with open(filepath, 'wb') as f:
                        f.write(await response.read())
                    logger.info("Gorsel basarili: Pollinations.ai")
                    return filepath
                else:
                    logger.warning(f"Pollinations.ai hata: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Pollinations.ai baglanti hatasi: {e}")
        return None
