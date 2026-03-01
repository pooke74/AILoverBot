"""Bot profil fotografini API ile ayarla + tanitim postlari olustur"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE = f"https://api.telegram.org/bot{TOKEN}"

# Logo dosyasi
LOGO_PATH = r"C:\Users\tolga\.gemini\antigravity\brain\e4893fba-0005-4d5a-ac91-1828af66f508\bot_profile_logo_1772372353736.png"

async def set_profile_photo():
    """Bot profil fotografini ayarla"""
    if not os.path.exists(LOGO_PATH):
        print(f"Logo bulunamadi: {LOGO_PATH}")
        return False
    
    async with aiohttp.ClientSession() as s:
        data = aiohttp.FormData()
        data.add_field('photo', open(LOGO_PATH, 'rb'), filename='logo.png', content_type='image/png')
        
        r = await s.post(f"{BASE}/setMyProfilePhoto", data=data)
        result = await r.json()
        
        if result.get('ok'):
            print("Profil fotografi ayarlandi!")
            return True
        else:
            print(f"Hata: {result}")
            # Bazi botlarda bu yetki olmayabilir
            return False

async def main():
    print("=== Bot Profil Fotografi ===")
    await set_profile_photo()

asyncio.run(main())
