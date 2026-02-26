"""Gemini image generation modeli testi"""
import asyncio
import aiohttp
import base64
import os
from dotenv import load_dotenv
load_dotenv()

async def test_model(model_name):
    key = os.getenv("GEMINI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": "Generate a photorealistic selfie of a beautiful 23 year old woman with dark brown wavy hair, hazel eyes, warm smile, natural makeup"}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"]
        }
    }
    
    print(f"\nTesting {model_name}...")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as r:
                print(f"  Status: {r.status}")
                if r.status == 200:
                    data = await r.json()
                    for cand in data.get('candidates', []):
                        for part in cand.get('content', {}).get('parts', []):
                            if 'inlineData' in part:
                                mime = part['inlineData'].get('mimeType', 'image/png')
                                ext = 'png' if 'png' in mime else 'jpg'
                                img_data = base64.b64decode(part['inlineData']['data'])
                                safe_name = model_name.replace("/", "_").replace(".", "_")
                                filepath = f"test_{safe_name}.{ext}"
                                with open(filepath, 'wb') as f:
                                    f.write(img_data)
                                print(f"  BASARILI! {filepath} ({len(img_data)} bytes)")
                                return True
                            elif 'text' in part:
                                print(f"  Text: {part['text'][:100]}")
                    # Check for blocked
                    if data.get('promptFeedback', {}).get('blockReason'):
                        print(f"  BLOCKED: {data['promptFeedback']['blockReason']}")
                    else:
                        print(f"  No image in response")
                else:
                    data = await r.json()
                    msg = data.get('error', {}).get('message', '')[:200]
                    print(f"  Hata: {msg}")
    except Exception as e:
        print(f"  Exception: {e}")
    return False

async def main():
    models = [
        "gemini-2.0-flash-exp-image-generation",
        "nano-banana-pro-preview",
        "gemini-2.5-flash-image",
        "gemini-3.1-flash-image-preview",
    ]
    for m in models:
        success = await test_model(m)
        if success:
            print(f"\n=== CALISAN MODEL: {m} ===")
            return

asyncio.run(main())
