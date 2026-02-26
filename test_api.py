"""OpenRouter guncel model testi - genis arama"""
import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()

async def test_models():
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Guncel OpenRouter model isimleri (2024-2026 arasi bilinen calisan modeller)
    models_to_test = [
        "deepseek/deepseek-chat",
        "deepseek/deepseek-r1:free",
        "google/gemma-2-9b-it:free",
        "meta-llama/llama-3.3-70b-instruct",
        "meta-llama/llama-3.2-3b-instruct:free",
        "mistralai/mistral-small-3.1-24b-instruct:free",
        "qwen/qwen-2.5-72b-instruct",
        "nousresearch/hermes-3-llama-3.1-405b",
        "openchat/openchat-7b:free",
        "microsoft/phi-3-mini-128k-instruct:free",
    ]
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "AILoverBot"
    }
    
    working = []
    
    for model in models_to_test:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Selam"}
            ],
            "max_tokens": 20
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    status = response.status
                    if status == 200:
                        import json
                        data = json.loads(await response.text())
                        content = data['choices'][0]['message']['content']
                        print(f"[OK] {model} -> {content[:60]}")
                        working.append(model)
                    else:
                        data = await response.text()
                        print(f"[XX] {model} -> {status}")
        except Exception as e:
            print(f"[ER] {model} -> {e}")
    
    print(f"\n=== CALISAN MODELLER ({len(working)}) ===")
    for m in working:
        print(f"  - {m}")
    return working

asyncio.run(test_models())
