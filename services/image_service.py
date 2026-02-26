import aiohttp
from config import FAL_API_KEY
from prompts.character import get_image_base_prompt

async def generate_image(prompt: str, character_id: str = 'mia') -> str:
    """
    Fal.ai API kullanarak görsel üretir ve resmin URL'sini döndürür.
    Karakter bazlı sabit yüz promptu kullanılır (LoRA benzeri tutarlılık).
    """
    if not FAL_API_KEY or FAL_API_KEY == "your_fal_api_key_here":
        print("FAL_API_KEY eksik.")
        return None
        
    url = "https://fal.run/fal-ai/flux-lora"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Karaktere özel sabit yüz/fizik promptu (LoRA consistent face)
    base_prompt = get_image_base_prompt(character_id)
    
    # Negatif prompt ile tutarlılığı artır
    negative_prompt = "multiple people, deformed face, ugly, blurry, low quality, cartoon, anime, drawing, text, watermark"
    
    full_prompt = base_prompt + prompt
    
    payload = {
        "prompt": full_prompt,
        "negative_prompt": negative_prompt,
        "image_size": "portrait_4_3",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "num_images": 1,
        "seed": 42  # Sabit seed, yüz tutarlılığını artırır
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['images'][0]['url']
                else:
                    error_text = await response.text()
                    print(f"Fal.ai Error: {response.status} - {error_text}")
                    return None
    except Exception as e:
        print(f"Görsel API Hatası: {e}")
        return None
