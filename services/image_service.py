import aiohttp
import logging
import base64
import os
import uuid
import urllib.parse
from config import FAL_API_KEY, GEMINI_API_KEY
from prompts.character import get_image_base_prompt

logger = logging.getLogger(__name__)

# Referans fotograf dizini
REF_DIR = "character_refs"

async def generate_image(prompt: str, character_id: str = 'mia', use_raw_prompt: bool = False) -> str:
    """
    Gorsel uretir. Referans foto varsa ayni yuz ile yeni poz olusturur.
    """
    if use_raw_prompt:
        full_prompt = prompt
    else:
        base_prompt = get_image_base_prompt(character_id)
        full_prompt = base_prompt + prompt
    
    # 1. Referans foto ile Gemini (TUTARLI YUZ!)
    result = await _call_gemini_with_reference(full_prompt, character_id)
    if result:
        return result
    
    # 2. Referanssiz Gemini (yedek)
    result = await _call_gemini_image(full_prompt)
    if result:
        return result
    
    # 3. Fal.ai
    if FAL_API_KEY and FAL_API_KEY != "your_fal_api_key_here":
        result = await _call_fal(full_prompt)
        if result:
            return result
    
    logger.error("Tum gorsel servisleri basarisiz!")
    return None

async def _ensure_reference_photo(character_id: str) -> str:
    """Karakter icin referans foto yoksa olusturur, varsa yolunu dondurur."""
    os.makedirs(REF_DIR, exist_ok=True)
    ref_path = os.path.join(REF_DIR, f"{character_id}_ref.png")
    
    if os.path.exists(ref_path):
        return ref_path
    
    # Referans foto olustur
    base_prompt = get_image_base_prompt(character_id)
    ref_prompt = f"{base_prompt} Professional portrait photo, looking directly at camera, clean white background, studio lighting. Face clearly visible, sharp focus on facial features."
    
    logger.info(f"Referans foto olusturuluyor: {character_id}")
    result = await _call_gemini_image(ref_prompt)
    
    if result and os.path.exists(result):
        # Olusturulan gorseli referans olarak kaydet
        import shutil
        shutil.copy2(result, ref_path)
        os.remove(result)
        logger.info(f"Referans foto kaydedildi: {ref_path}")
        return ref_path
    
    logger.warning(f"Referans foto olusturulamadi: {character_id}")
    return None

async def _call_gemini_with_reference(full_prompt: str, character_id: str) -> str:
    """Referans foto ile Gemini'den tutarli yuz uretimi."""
    if not GEMINI_API_KEY:
        return None
    
    ref_path = await _ensure_reference_photo(character_id)
    if not ref_path or not os.path.exists(ref_path):
        return None
    
    # Referans fotoyu oku
    with open(ref_path, 'rb') as f:
        ref_data = base64.b64encode(f.read()).decode()
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [
                {"inlineData": {"mimeType": "image/png", "data": ref_data}},
                {"text": f"Using the EXACT SAME person shown in the reference photo above (same face, same hair, same features), generate a new photo of her: {full_prompt}. The face and physical features MUST be identical to the reference."}
            ]
        }],
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
                                logger.info(f"Gorsel basarili: Gemini + referans ({character_id}, {len(img_data)} bytes)")
                                return filepath
                    logger.warning("Gemini referans: gorsel bulunamadi response icinde")
                    return None
                else:
                    error_text = await response.text()
                    logger.warning(f"Gemini referans hata: {response.status} - {error_text[:150]}")
                    return None
    except Exception as e:
        logger.error(f"Gemini referans baglanti hatasi: {e}")
        return None

async def _call_gemini_image(full_prompt: str) -> str:
    """Gemini 2.0 Flash Image Generation ile gorsel uret (referanssiz)."""
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
        "num_images": 1
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
