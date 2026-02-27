"""Tum karakterler icin referans fotograf olustur"""
import asyncio
import aiohttp
import base64
import os
from dotenv import load_dotenv
load_dotenv()

CHARACTERS = {
    "mia": "Professional portrait photo of a beautiful 23 year old Mediterranean woman with long dark brown wavy hair, hazel-green eyes, light olive skin, natural glowing makeup, warm genuine smile. Looking directly at camera. Clean background. Photorealistic.",
    "elif": "Professional portrait photo of a stunning 27 year old woman with sleek straight black hair, piercing green eyes, fair porcelain skin, bold red lipstick, sharp jawline, confident powerful gaze. Looking directly at camera. Clean background. Photorealistic.",
    "yuki": "Professional portrait photo of a cute 20 year old half-Japanese half-Turkish girl with short black bob hair with straight bangs, big dark brown doe eyes, soft pale skin, shy cute smile, blushing cheeks. Looking directly at camera. Clean background. Photorealistic.",
    "defne": "Professional portrait photo of a glamorous 25 year old Turkish woman with long blonde highlighted wavy hair, bright blue eyes, perfect contoured makeup, pouty glossy lips, golden tan skin. Looking directly at camera. Clean background. Photorealistic.",
}

async def generate_ref(name, prompt):
    key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp-image-generation:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Generate this exact image: {prompt}"}]}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]}
    }
    
    print(f"  {name}...", end=" ", flush=True)
    async with aiohttp.ClientSession() as s:
        async with s.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as r:
            if r.status == 200:
                data = await r.json()
                for cand in data.get('candidates', []):
                    for part in cand.get('content', {}).get('parts', []):
                        if 'inlineData' in part:
                            img_data = base64.b64decode(part['inlineData']['data'])
                            os.makedirs("character_refs", exist_ok=True)
                            filepath = f"character_refs/{name}_ref.png"
                            with open(filepath, 'wb') as f:
                                f.write(img_data)
                            print(f"OK ({len(img_data)} bytes)")
                            return
                print("gorsel yok")
            else:
                print(f"HATA {r.status}")

async def main():
    print("Referans fotograflar olusturuluyor...\n")
    for name, prompt in CHARACTERS.items():
        ref_path = f"character_refs/{name}_ref.png"
        if os.path.exists(ref_path):
            print(f"  {name}... ZATEN VAR, atlaniyor")
            continue
        await generate_ref(name, prompt)
    print("\nTamamlandi!")

asyncio.run(main())
