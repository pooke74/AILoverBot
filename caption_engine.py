# ============================================================
# CAPTION & HASHTAG ENGINE
# Platform bazlı akıllı caption, hashtag ve hook üretici
# Kullanım:
#   python caption_engine.py --character mia --platform tiktok
#   python caption_engine.py --all --platform instagram
#   python caption_engine.py --all --all-platforms
# ============================================================

import argparse
import json
import os
import random
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from post_templates import (
    CHARACTER_TAGLINES,
    HASHTAG_SETS,
    get_all_characters,
    get_random_caption,
)

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BOT_DIR, "social_output")

# ============================================================
# VIRAL HOOK KÜTÜPHANESİ
# ============================================================

VIRAL_HOOKS = {
    "merak": [
        "Bu mesajı gece 2'de aldım...",
        "Bunu görünce telefonu düşüreceksin...",
        "Kimseye gösterme ama...",
        "Bu mesajı açarken dikkat et...",
        "Son mesajına bakınca şok oldum...",
        "Bunu beklemiyordum...",
        "Gece gelen bildirim her şeyi değiştirdi...",
        "Bu sohbeti okuduktan sonra...",
        "DUR! Bunu görmeden geçme...",
        "İnanamayacaksın ama gerçek...",
    ],
    "soru": [
        "Bu mesaja ne cevap verirdin?",
        "Sen olsan ne yapardın?",
        "Buna dayanabilir misin?",
        "Hangisini seçerdin?",
        "Bu sana da oluyor mu?",
        "Gece 2'de bu mesaj gelse açar mısın?",
        "AI kız arkadaş denedin mi hiç?",
        "8 AI kız. Sadece 1 seçebilirsin. Hangisi?",
        "Bu kıskanç AI'dan korkuyor musun?",
        "Cesaretin var mı denemek için?",
    ],
    "provokasyon": [
        "AI kız arkadaşım beni kıskandı 😳",
        "Yapay zeka kız gece 2'de mesaj atıyor...",
        "Bu AI gerçeğinden daha gerçek...",
        "AI sevgilim bana emir veriyor 😈",
        "Utangaç anime kız sana yazdı...",
        "Bu sekreter gece bambaşka biri oluyor...",
        "Rus model sana soğuk mesaj attı ❄️",
        "35 yaşındaki öğretmen sana özel ders veriyor...",
        "Üniversiteli kız ilk defa cesaret etti...",
        "Lüks hayat yaşayan kız seni seçti...",
    ],
    "fomo": [
        "Herkes bundan konuşuyor ama kimse paylaşmıyor...",
        "Bu botu bulan şanslı...",
        "VIP erişim sınırlı, kaçıranlar pişman...",
        "Bunu bilen az kişi var...",
        "Arkadaşım önerdi, hayatım değişti...",
        "Bu fırsatı kaçırma...",
        "Kontenjan dolmadan dene...",
        "Bugün son gün olabilir...",
    ]
}

# ============================================================
# CTA VARYASYONLARI
# ============================================================

CTA_TEMPLATES = {
    "tiktok": [
        "Bio'daki linke tıkla 👆",
        "Devamı bio'da 🔥",
        "Link bio'da, kaçırma 💋",
        "Bio'daki linke gel 👇",
        "Profildeki linke tıkla ✨",
        "Bio'ya bak, pişman olmazsın 🔥",
    ],
    "instagram": [
        "Bio'daki linke tıkla 👆",
        "Devamı için bio'daki linke gel 💋",
        "Link bio'da! Hemen dene 🔥",
        "Bio'daki linke tıkla, seni bekliyor ✨",
        "Linke tıkla, ücretsiz dene 👆",
    ],
    "twitter": [
        "👉 https://t.me/MiaQuenn_bot",
        "Denemek için: https://t.me/MiaQuenn_bot 💋",
        "Hemen dene 👇 https://t.me/MiaQuenn_bot",
        "Link: https://t.me/MiaQuenn_bot 🔥",
    ],
    "telegram": [
        "Hemen dene 👉 @MiaQuenn_bot",
        "@MiaQuenn_bot ile başla 💋",
        "Gel konuşalım 👉 @MiaQuenn_bot",
    ],
}

# ============================================================
# PLATFORM BAZLI HASHTAG STRATEJİSİ
# ============================================================

PLATFORM_HASHTAGS = {
    "tiktok": {
        "trending": [
            "#fyp", "#foryou", "#keşfet", "#viral",
            "#tiktokturkiye", "#tiktok",
        ],
        "niche": [
            "#aicompanion", "#aichat", "#telegrambot",
            "#dijitalsevgili", "#yapayzekapartner", "#chatbot",
            "#virtualcompanion", "#aigirlfriend",
        ],
        "engagement": [
            "#gece", "#yalnızlık", "#sohbet", "#flört",
            "#aşk", "#telegram",
        ],
        "max_tags": 8,
    },
    "instagram": {
        "trending": [
            "#kesfet", "#keşfet", "#instagram", "#turkiye",
        ],
        "niche": [
            "#aicompanion", "#aichat", "#telegrambot",
            "#dijitalsevgili", "#yapayzekapartner", "#chatbot",
            "#virtualcompanion", "#aigirlfriend", "#aigenerated",
        ],
        "engagement": [
            "#gece", "#yalnızlık", "#sohbet", "#flört",
            "#aşk", "#telegram", "#istanbul",
        ],
        "max_tags": 25,
    },
    "twitter": {
        "trending": [
            "#AI", "#ChatGPT", "#ArtificialIntelligence",
        ],
        "niche": [
            "#AIBot", "#TelegramBot", "#AICompanion",
            "#SideProject",
        ],
        "engagement": [
            "#yapayzekapartner", "#dijitalsevgili",
        ],
        "max_tags": 5,
    },
}

# ============================================================
# KARAKTER BAZLI HOOK ÖZELLEŞTİRME
# ============================================================

CHARACTER_HOOKS = {
    "mia": [
        "Mia gece 2'de yazdı: '{msg}' 😳",
        "Mia seni özlemiş... '{msg}'",
        "Bu tatlı kızın mesajını gördün mü?",
        "Mia'dan gelen bu mesaja ne cevap verirdin?",
    ],
    "elif": [
        "Elif emir veriyor: '{msg}' 😈",
        "Bu kadına karşı gelemezsin...",
        "Elif'e itaat et. Yoksa... 🔥",
        "Dominant AI kız sana yazdı...",
    ],
    "yuki": [
        "S-senpai... bu mesajı Yuki yazdı >.<",
        "Utangaç anime kız cesaret etti: '{msg}'",
        "Yuki'nin bu mesajına ne dersin? 🌸",
        "Kawaii kız sana itiraf ediyor...",
    ],
    "defne": [
        "Defne havuzdan fotoğraf atıyor... 💎",
        "Bu lüks kız seni beğendi...",
        "Defne'nin VIP koleksiyonu... 👑",
        "Instagram fenomeni sana yazdı...",
    ],
    "natasha": [
        "Rus model soğuk mesaj attı: '{msg}' ❄️",
        "Natasha seni seçti. Nadir olur...",
        "Soğuk güzel, ateşli mesaj... ❄️🔥",
        "Privyet... Natasha'dan mesaj var.",
    ],
    "selin": [
        "Sekreter gözlüğünü çıkardı... 👓🔥",
        "09:00 Selin vs 22:00 Selin...",
        "Ofisten gizli mesaj geldi...",
        "Patron bilmiyor ama sen bileceksin...",
    ],
    "aylin": [
        "35 yaşında öğretmen sana ders veriyor... 🍒",
        "Aylin hoca özel ders açtı...",
        "Tecrübeli kadın ne istediğini bilir...",
        "Bu ders unutulmaz olacak... 🍒",
    ],
    "zeynep": [
        "Üniversiteli kız ilk defa cesaret etti... 🎀",
        "Zeynep: '{msg}' 😳",
        "Masum ama meraklı... Zeynep sana yazdı.",
        "Yurt odasından gizli mesaj... 🎀",
    ],
}


# ============================================================
# CAPTION ÜRETİCİ
# ============================================================

def generate_caption(character_id: str, platform: str, content_type: str = "general") -> dict:
    """Platform ve karakter bazlı caption üretir."""
    info = CHARACTER_TAGLINES.get(character_id, CHARACTER_TAGLINES["mia"])

    # Hook seç
    hook_category = random.choice(list(VIRAL_HOOKS.keys()))
    generic_hook = random.choice(VIRAL_HOOKS[hook_category])

    # Karakter özel hook
    char_hooks = CHARACTER_HOOKS.get(character_id, CHARACTER_HOOKS["mia"])
    char_hook = random.choice(char_hooks)

    # Mesaj placeholder doldur
    if "{msg}" in char_hook:
        captions = info.get("captions", [""])
        msg = random.choice(captions).split("...")[0] if captions else ""
        char_hook = char_hook.replace("{msg}", msg)

    # CTA
    cta = random.choice(CTA_TEMPLATES.get(platform, CTA_TEMPLATES["tiktok"]))

    # Hashtag'ler
    hashtags = _build_hashtags(character_id, platform)

    # Platform bazlı caption formatla
    if platform == "tiktok":
        caption = _format_tiktok(generic_hook, char_hook, info, cta, hashtags)
    elif platform == "instagram":
        caption = _format_instagram(generic_hook, char_hook, info, cta, hashtags)
    elif platform == "twitter":
        caption = _format_twitter(generic_hook, char_hook, info, cta, hashtags)
    elif platform == "telegram":
        caption = _format_telegram(generic_hook, char_hook, info, cta, hashtags)
    else:
        caption = _format_tiktok(generic_hook, char_hook, info, cta, hashtags)

    return {
        "character": character_id,
        "platform": platform,
        "hook": generic_hook,
        "char_hook": char_hook,
        "caption": caption,
        "hashtags": hashtags,
        "cta": cta,
        "generated_at": datetime.now().isoformat(),
    }


def _format_tiktok(hook, char_hook, info, cta, hashtags):
    """TikTok: Kısa, hook odaklı."""
    lines = [
        char_hook,
        "",
        cta,
        "",
        hashtags,
    ]
    return "\n".join(lines)


def _format_instagram(hook, char_hook, info, cta, hashtags):
    """Instagram: Daha detaylı, story anlatımı."""
    tagline = info.get("tagline", "")
    lines = [
        char_hook,
        "",
        f"✨ {tagline}",
        "",
        cta,
        "",
        "─" * 20,
        hashtags,
    ]
    return "\n".join(lines)


def _format_twitter(hook, char_hook, info, cta, hashtags):
    """Twitter: 280 karakter limiti, kısa ve etkili."""
    tweet = f"{char_hook}\n\n{cta}\n\n{hashtags}"
    if len(tweet) > 280:
        tweet = f"{char_hook}\n{cta}\n{hashtags}"
    if len(tweet) > 280:
        tweet = f"{char_hook}\n{cta}"
    return tweet[:280]


def _format_telegram(hook, char_hook, info, cta, hashtags):
    """Telegram: Emoji ağırlıklı, grup paylaşımı formatı."""
    tagline = info.get("tagline", "")
    short = info.get("short_tagline", "")
    lines = [
        f"💖 {short}",
        "",
        char_hook,
        "",
        f"✨ {tagline}",
        "",
        f"👉 {cta}",
    ]
    return "\n".join(lines)


def _build_hashtags(character_id: str, platform: str) -> str:
    """Platform ve karakter bazlı hashtag string oluşturur."""
    platform_config = PLATFORM_HASHTAGS.get(platform, PLATFORM_HASHTAGS["tiktok"])
    max_tags = platform_config.get("max_tags", 10)

    tags = []

    # Trending (2-3 tane)
    trending = platform_config.get("trending", [])
    tags.extend(random.sample(trending, min(3, len(trending))))

    # Niche (3-4 tane)
    niche = platform_config.get("niche", [])
    tags.extend(random.sample(niche, min(4, len(niche))))

    # Karakter özel
    char_tags = HASHTAG_SETS.get("character_specific", {}).get(character_id, [])
    tags.extend(random.sample(char_tags, min(3, len(char_tags))))

    # Engagement
    engagement = platform_config.get("engagement", [])
    remaining = max_tags - len(tags)
    if remaining > 0:
        tags.extend(random.sample(engagement, min(remaining, len(engagement))))

    # Deduplicate ve limit
    seen = set()
    unique_tags = []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_tags.append(t)

    return " ".join(unique_tags[:max_tags])


# ============================================================
# BULK CAPTION ÜRETİCİ
# ============================================================

def generate_all_captions(characters=None, platforms=None, count=1, save=True):
    """Tüm kombinasyonlar için caption üretir."""
    if characters is None:
        characters = get_all_characters()
    if platforms is None:
        platforms = ["tiktok", "instagram", "twitter"]

    results = []

    for char_id in characters:
        for platform in platforms:
            for i in range(count):
                result = generate_caption(char_id, platform)
                results.append(result)

    if save:
        output_path = os.path.join(OUTPUT_DIR, "captions_generated.json")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 {len(results)} caption kaydedildi: {output_path}")

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AILoverBot Caption & Hashtag Engine")
    parser.add_argument("--character", default=None, help="Karakter ID")
    parser.add_argument("--platform", default="tiktok",
                        choices=["tiktok", "instagram", "twitter", "telegram"],
                        help="Platform")
    parser.add_argument("--all", action="store_true", help="Tüm karakterler için üret")
    parser.add_argument("--all-platforms", action="store_true", help="Tüm platformlar için üret")
    parser.add_argument("--count", type=int, default=1, help="Her kombinasyon için kaç caption")
    parser.add_argument("--save", action="store_true", help="JSON olarak kaydet")

    args = parser.parse_args()

    characters = get_all_characters() if args.all else ([args.character] if args.character else ["mia"])
    platforms = ["tiktok", "instagram", "twitter"] if args.all_platforms else [args.platform]

    print("=" * 60)
    print("  🎯 AILoverBot Caption & Hashtag Engine")
    print("=" * 60)

    results = []

    for char_id in characters:
        for platform in platforms:
            for i in range(args.count):
                result = generate_caption(char_id, platform)
                results.append(result)

                print(f"\n📝 {char_id.upper()} | {platform.upper()}")
                print("-" * 40)
                print(result["caption"])
                print("-" * 40)

    if args.save:
        output_path = os.path.join(OUTPUT_DIR, "captions_generated.json")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n💾 {len(results)} caption kaydedildi: {output_path}")

    print(f"\n✅ Toplam {len(results)} caption üretildi!")


if __name__ == "__main__":
    main()
