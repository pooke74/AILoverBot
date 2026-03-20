import aiohttp
import logging
import base64
import os
import uuid
from config import FAL_API_KEY, GEMINI_API_KEY
from prompts.character import get_image_base_prompt

logger = logging.getLogger(__name__)

# Referans fotograf dizini
REF_DIR = "character_refs"

# ============================================================
# YAKINLIK SEVIYESINE GORE GORSEL PROMPT EKLEMELERI
# Seviye arttikca fotograflar daha cesur olur
# ============================================================
INTIMACY_IMAGE_MODIFIERS = {
    1: "Casual, friendly pose. Fully clothed in casual daily outfit.",
    2: "Flirty pose, playful expression. Casual stylish outfit, showing some skin.",
    3: "Seductive pose, bedroom eyes. Tight fitting clothes, low neckline, showing cleavage.",
    4: "Very seductive, intimate pose. Lingerie, underwear, or very revealing outfit. Sensual expression.",
    5: "Extremely intimate and seductive. Minimal clothing, lingerie, bikini. Highly provocative pose, passionate expression.",
}

async def generate_image(prompt: str, character_id: str = 'mia', 
                         use_raw_prompt: bool = False, intimacy_level: int = 1) -> str:
    """
    Gorsel uretir. Yakinlik seviyesine gore cesaret artar.
    """
    if use_raw_prompt:
        full_prompt = prompt
    else:
        base_prompt = get_image_base_prompt(character_id)
        intimacy_mod = INTIMACY_IMAGE_MODIFIERS.get(min(intimacy_level, 5), "")
        full_prompt = f"{base_prompt} {prompt}. {intimacy_mod}"
    
    # Kalite eklemeleri
    quality_suffix = " Ultra photorealistic, shot on Canon EOS R5, 85mm lens, f/1.8, natural lighting, 8K resolution, skin texture detail, no AI artifacts."
    full_prompt += quality_suffix
    
    # 1. Fal.ai (en kaliteli, sansursuz)
    if FAL_API_KEY and FAL_API_KEY != "your_fal_api_key_here":
        result = await _call_fal(full_prompt)
        if result:
            return result
    
    # 2. Referans foto ile Gemini
    result = await _call_gemini_with_reference(full_prompt, character_id)
    if result:
        return result
    
    # 3. Referanssiz Gemini (yedek)
    result = await _call_gemini_image(full_prompt)
    if result:
        return result
    
    logger.error("Tum gorsel servisleri basarisiz!")
    return None

async def _ensure_reference_photo(character_id: str) -> str:
    """Karakter icin referans foto yoksa olusturur."""
    os.makedirs(REF_DIR, exist_ok=True)
    ref_path = os.path.join(REF_DIR, f"{character_id}_ref.png")
    
    if os.path.exists(ref_path):
        return ref_path
    
    base_prompt = get_image_base_prompt(character_id)
    ref_prompt = f"{base_prompt} Professional portrait photo, looking directly at camera, clean white background, studio lighting. Face clearly visible, sharp focus on facial features."
    
    logger.info(f"Referans foto olusturuluyor: {character_id}")
    result = await _call_gemini_image(ref_prompt)
    
    if result and os.path.exists(result):
        import shutil
        shutil.copy2(result, ref_path)
        os.remove(result)
        logger.info(f"Referans foto kaydedildi: {ref_path}")
        return ref_path
    
    logger.warning(f"Referans foto olusturulamadi: {character_id}")
    return None

async def _call_fal(full_prompt: str) -> str:
    """Fal.ai Flux ile yuksek kalite gorsel uret."""
    negative_prompt = (
        "multiple people, extra limbs, deformed face, ugly, blurry, low quality, "
        "cartoon, anime, drawing, text, watermark, logo, "
        "bad anatomy, bad proportions, extra fingers, mutated hands"
    )
    
    url = "https://fal.run/fal-ai/flux-lora"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "image_size": "portrait_4_3",
        "num_inference_steps": 35,
        "guidance_scale": 4.0,
        "num_images": 1,
        "enable_safety_checker": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, 
                                    timeout=aiohttp.ClientTimeout(total=60)) as response:
                if response.status == 200:
                    data = await response.json()
                    img_url = data['images'][0]['url']
                    
                    # URL'yi indirip temp dosya olarak kaydet
                    async with session.get(img_url) as img_resp:
                        if img_resp.status == 200:
                            img_data = await img_resp.read()
                            os.makedirs("temp_images", exist_ok=True)
                            filepath = f"temp_images/{uuid.uuid4()}.jpg"
                            with open(filepath, 'wb') as f:
                                f.write(img_data)
                            logger.info(f"Gorsel basarili: Fal.ai Flux ({len(img_data)} bytes)")
                            return filepath
                    
                    # URL direkt dondur (indirilemezse)
                    logger.info("Gorsel basarili: Fal.ai (URL)")
                    return img_url
                else:
                    error_text = await response.text()
                    logger.warning(f"Fal.ai hata: {response.status} - {error_text[:150]}")
                    return None
    except Exception as e:
        logger.error(f"Fal.ai baglanti hatasi: {e}")
        return None

async def _call_gemini_with_reference(full_prompt: str, character_id: str) -> str:
    """Referans foto ile Gemini'den tutarli yuz uretimi."""
    if not GEMINI_API_KEY:
        return None
    
    ref_path = await _ensure_reference_photo(character_id)
    if not ref_path or not os.path.exists(ref_path):
        return None
    
    with open(ref_path, 'rb') as f:
        ref_data = base64.b64encode(f.read()).decode()
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={GEMINI_API_KEY}"
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
            async with session.post(url, headers=headers, json=payload, 
                                    timeout=aiohttp.ClientTimeout(total=60)) as response:
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
                                logger.info(f"Gorsel basarili: Gemini + referans ({character_id})")
                                return filepath
                    return None
                else:
                    error_text = await response.text()
                    logger.warning(f"Gemini referans hata: {response.status} - {error_text[:200]}")
                    return None
    except Exception as e:
        logger.error(f"Gemini referans hatasi: {e}")
        return None

async def _call_gemini_image(full_prompt: str) -> str:
    """Gemini 2.0 Flash Image Generation (referanssiz yedek)."""
    if not GEMINI_API_KEY:
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Generate this image: {full_prompt}"}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, 
                                    timeout=aiohttp.ClientTimeout(total=60)) as response:
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
                                logger.info(f"Gorsel basarili: Gemini ({len(img_data)} bytes)")
                                return filepath
                    return None
                else:
                    return None
    except Exception as e:
        logger.error(f"Gemini Image hatasi: {e}")
        return None
