import asyncio, aiohttp, os
from dotenv import load_dotenv
load_dotenv()

async def update_commands():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    async with aiohttp.ClientSession() as s:
        r = await s.post(f"https://api.telegram.org/bot{TOKEN}/setMyCommands", json={
            "commands": [
                {"command": "menu", "description": "Ana menu"},
                {"command": "karakterler", "description": "Karakter sec"},
                {"command": "hediye", "description": "Hediye gonder"},
                {"command": "profile", "description": "Profilim"},
                {"command": "buy", "description": "Kredi yukle"},
                {"command": "davet", "description": "Arkadas davet et"},
                {"command": "sexting", "description": "Sexting Modu (+18)"},
                {"command": "help", "description": "Yardim"},
            ]
        })
        d = await r.json()
        print("Komutlar OK" if d.get("ok") else f"HATA: {d}")

asyncio.run(update_commands())
