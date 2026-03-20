# ============================================================
# CONTENT CALENDAR & PACKAGER
# İçerik takvimi yönetimi ve platform-ready paketleme
# Kullanım:
#   python content_calendar.py --generate-week
#   python content_calendar.py --show-today
#   python content_calendar.py --show-week
#   python content_calendar.py --package-today
# ============================================================

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from post_templates import get_all_characters, CHARACTER_TAGLINES
from caption_engine import generate_caption, CTA_TEMPLATES

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BOT_DIR, "social_output")
CALENDAR_DIR = os.path.join(OUTPUT_DIR, "calendar")

GUN_ISIMLERI = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# ============================================================
# POST SAAT PLANLARI
# ============================================================

POSTING_SCHEDULE = {
    "tiktok": [
        {"time": "12:00", "note": "Öğle molası — engagement yüksek"},
        {"time": "18:00", "note": "İş çıkışı — scroll zamanı"},
        {"time": "22:00", "note": "Gece — en yüksek engagement"},
    ],
    "instagram": [
        {"time": "09:00", "note": "Sabah — feed post"},
        {"time": "13:00", "note": "Öğle — story"},
        {"time": "20:00", "note": "Akşam — reels"},
    ],
    "twitter": [
        {"time": "10:00", "note": "Sabah — tweet"},
        {"time": "14:00", "note": "Öğle — engagement tweet"},
        {"time": "21:00", "note": "Gece — thread"},
    ],
}

# ============================================================
# HAFTALIK DETAYLI PLAN
# ============================================================

DETAILED_WEEKLY_PLAN = {
    0: {  # Pazartesi
        "theme": "🌹 Romantik Başlangıç",
        "slots": [
            {"time": "12:00", "platform": "tiktok", "character": "mia", "type": "chat_video",
             "scenario": "gece_mesaji", "note": "Haftanın açılışı — Mia ile romantik hook"},
            {"time": "18:00", "platform": "tiktok", "character": "elif", "type": "notification",
             "note": "İş çıkışı — Elif bildirim mockup"},
            {"time": "20:00", "platform": "instagram", "character": "mia", "type": "static_post",
             "note": "Feed post — Mia portre + tagline"},
            {"time": "22:00", "platform": "tiktok", "character": "mia", "type": "notification",
             "note": "Gece — merak uyandırıcı bildirim"},
        ]
    },
    1: {  # Salı
        "theme": "🌸 Anime & Lüks Dünya",
        "slots": [
            {"time": "12:00", "platform": "tiktok", "character": "yuki", "type": "showcase_video",
             "note": "Öğle — Yuki tanıtım videosu"},
            {"time": "18:00", "platform": "tiktok", "character": "defne", "type": "chat_video",
             "scenario": "havuz", "note": "Defne havuz temalı chat"},
            {"time": "20:00", "platform": "instagram", "character": "yuki", "type": "static_post",
             "note": "Feed post — Yuki kawaii portre"},
            {"time": "22:00", "platform": "tiktok", "character": "defne", "type": "notification",
             "note": "Gece — Defne VIP bildirimi"},
        ]
    },
    2: {  # Çarşamba
        "theme": "❄️ Egzotik & Gizem",
        "slots": [
            {"time": "12:00", "platform": "tiktok", "character": "natasha", "type": "chat_video",
             "scenario": "soguk_sicak", "note": "Natasha soğuk-sıcak dinamiği"},
            {"time": "18:00", "platform": "tiktok", "character": "selin", "type": "notification",
             "note": "Selin ofisten gizli bildirim"},
            {"time": "20:00", "platform": "instagram", "character": "natasha", "type": "static_post",
             "note": "Feed post — Natasha egzotik portre"},
            {"time": "21:00", "platform": "twitter", "character": "natasha", "type": "tweet",
             "note": "Twitter — Natasha hook tweet"},
        ]
    },
    3: {  # Perşembe
        "theme": "🔥 Dönüşüm & Tecrübe",
        "slots": [
            {"time": "12:00", "platform": "tiktok", "character": "selin", "type": "chat_video",
             "scenario": "ofis_gizli", "note": "Selin ofis → gece dönüşümü"},
            {"time": "18:00", "platform": "tiktok", "character": "aylin", "type": "showcase_video",
             "note": "Aylin tanıtım — tecrübeli kadın"},
            {"time": "20:00", "platform": "instagram", "character": "aylin", "type": "static_post",
             "note": "Feed post — Aylin olgun portre"},
            {"time": "22:00", "platform": "tiktok", "character": "aylin", "type": "notification",
             "note": "Gece — Aylin özel ders bildirimi"},
        ]
    },
    4: {  # Cuma
        "theme": "🎀 Masumiyet & Keşif",
        "slots": [
            {"time": "12:00", "platform": "tiktok", "character": "zeynep", "type": "chat_video",
             "scenario": "yurt_yalniz", "note": "Zeynep yurt odası senaryosu"},
            {"time": "18:00", "platform": "tiktok", "character": "zeynep", "type": "notification",
             "note": "Zeynep masum bildirim"},
            {"time": "20:00", "platform": "instagram", "character": "zeynep", "type": "static_post",
             "note": "Feed post — Zeynep kampüs portre"},
            {"time": "22:00", "platform": "tiktok", "character": "mia", "type": "chat_video",
             "scenario": "kiskanclik", "note": "Cuma gecesi — Mia kıskanç mesaj"},
        ]
    },
    5: {  # Cumartesi
        "theme": "👑 VIP Katalog Günü",
        "slots": [
            {"time": "13:00", "platform": "tiktok", "character": "elif", "type": "chat_video",
             "scenario": "itaat", "note": "Elif dominant tema"},
            {"time": "17:00", "platform": "tiktok", "character": "elif", "type": "showcase_video",
             "note": "Elif VIP tanıtım"},
            {"time": "20:00", "platform": "instagram", "character": "defne", "type": "static_post",
             "note": "Feed post — Defne lüks portre"},
            {"time": "23:00", "platform": "tiktok", "character": "yuki", "type": "chat_video",
             "scenario": "utangac_itiraf", "note": "Gece — Yuki cesur itiraf"},
        ]
    },
    6: {  # Pazar
        "theme": "✨ Engagement & Recap",
        "slots": [
            {"time": "14:00", "platform": "tiktok", "character": "mia", "type": "showcase_video",
             "note": "Mia en popüler — tanıtım videosu"},
            {"time": "18:00", "platform": "instagram", "character": "elif", "type": "static_post",
             "note": "Feed post — Elif dominant portre"},
            {"time": "20:00", "platform": "twitter", "character": "mia", "type": "thread",
             "note": "Haftalık recap thread"},
            {"time": "22:00", "platform": "tiktok", "character": "natasha", "type": "notification",
             "note": "Pazar gecesi — Natasha soğuk bildirim"},
        ]
    },
}


# ============================================================
# TAKVIM ÜRETİCİ
# ============================================================

def generate_week_calendar(start_date=None):
    """Haftalık takvim JSON dosyası üretir."""
    if start_date is None:
        start_date = datetime.now()

    weekday = start_date.weekday()
    # Pazartesi'den başlat
    monday = start_date - timedelta(days=weekday)

    calendar_data = {
        "week_start": monday.strftime("%Y-%m-%d"),
        "week_end": (monday + timedelta(days=6)).strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "days": [],
    }

    for day_offset in range(7):
        day_date = monday + timedelta(days=day_offset)
        day_num = day_offset  # 0=Pazartesi
        day_plan = DETAILED_WEEKLY_PLAN.get(day_num, {"theme": "Serbest", "slots": []})

        day_data = {
            "date": day_date.strftime("%Y-%m-%d"),
            "day_name": GUN_ISIMLERI[day_num],
            "theme": day_plan["theme"],
            "posts": [],
        }

        for slot in day_plan["slots"]:
            # Caption üret
            platform = slot["platform"]
            char_id = slot["character"]
            caption_data = generate_caption(char_id, platform)

            post = {
                "time": slot["time"],
                "platform": platform,
                "character": char_id,
                "type": slot["type"],
                "scenario": slot.get("scenario"),
                "note": slot.get("note", ""),
                "caption": caption_data["caption"],
                "hashtags": caption_data["hashtags"],
                "cta": caption_data["cta"],
                "status": "planned",  # planned / ready / posted
            }
            day_data["posts"].append(post)

        calendar_data["days"].append(day_data)

    # Kaydet
    os.makedirs(CALENDAR_DIR, exist_ok=True)
    cal_path = os.path.join(CALENDAR_DIR, f"week_{monday.strftime('%Y%m%d')}.json")
    with open(cal_path, "w", encoding="utf-8") as f:
        json.dump(calendar_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Haftalık takvim oluşturuldu: {cal_path}")
    return calendar_data, cal_path


def show_today():
    """Bugünün içerik planını gösterir."""
    today = datetime.now()
    weekday = today.weekday()
    day_plan = DETAILED_WEEKLY_PLAN.get(weekday, {"theme": "Serbest", "slots": []})

    print(f"\n{'=' * 60}")
    print(f"  📅 Bugün: {GUN_ISIMLERI[weekday]} {today.strftime('%d/%m/%Y')}")
    print(f"  🎯 Tema: {day_plan['theme']}")
    print(f"{'=' * 60}\n")

    if not day_plan["slots"]:
        print("  Bugün planlanmış post yok.\n")
        return

    for i, slot in enumerate(day_plan["slots"], 1):
        char_id = slot["character"]
        info = CHARACTER_TAGLINES.get(char_id, {})
        platform_emoji = {"tiktok": "📱", "instagram": "📸", "twitter": "🐦"}.get(slot["platform"], "📋")

        print(f"  {i}. ⏰ {slot['time']} | {platform_emoji} {slot['platform'].upper()}")
        print(f"     👤 {char_id.upper()} | {slot['type']}")
        if slot.get("scenario"):
            print(f"     📝 Senaryo: {slot['scenario']}")
        print(f"     💡 {slot.get('note', '')}")

        # Hızlı caption önizleme
        caption_data = generate_caption(char_id, slot["platform"])
        first_line = caption_data["caption"].split("\n")[0]
        print(f"     📣 Hook: {first_line}")
        print()


def show_week():
    """Haftalık takvim özetini gösterir."""
    today = datetime.now()
    weekday = today.weekday()
    monday = today - timedelta(days=weekday)

    print(f"\n{'=' * 60}")
    print(f"  📅 Haftalık İçerik Takvimi")
    print(f"  {monday.strftime('%d/%m')} - {(monday + timedelta(days=6)).strftime('%d/%m/%Y')}")
    print(f"{'=' * 60}\n")

    total_posts = 0

    for day_offset in range(7):
        day_date = monday + timedelta(days=day_offset)
        day_num = day_offset
        day_plan = DETAILED_WEEKLY_PLAN.get(day_num, {"theme": "Serbest", "slots": []})
        is_today = day_date.date() == today.date()

        marker = " 👈 BUGÜN" if is_today else ""
        print(f"  {'🟢' if is_today else '⚪'} {GUN_ISIMLERI[day_num]} ({day_date.strftime('%d/%m')}) — {day_plan['theme']}{marker}")

        for slot in day_plan["slots"]:
            platform_emoji = {"tiktok": "📱", "instagram": "📸", "twitter": "🐦"}.get(slot["platform"], "📋")
            print(f"      {slot['time']} {platform_emoji} {slot['character'].upper()} → {slot['type']}")
            total_posts += 1

        print()

    print(f"  📊 Toplam: {total_posts} post / hafta")
    print(f"  📱 Günlük ortalama: {total_posts / 7:.0f} post\n")


def package_today():
    """Bugünün içeriklerini platform-ready paketler."""
    today = datetime.now()
    weekday = today.weekday()
    day_plan = DETAILED_WEEKLY_PLAN.get(weekday, {"theme": "Serbest", "slots": []})

    if not day_plan["slots"]:
        print("  Bugün planlanmış post yok.")
        return

    package_dir = os.path.join(OUTPUT_DIR, "packages", today.strftime("%Y%m%d"))
    os.makedirs(package_dir, exist_ok=True)

    packages = []
    for i, slot in enumerate(day_plan["slots"], 1):
        char_id = slot["character"]
        platform = slot["platform"]
        caption_data = generate_caption(char_id, platform)

        pkg = {
            "order": i,
            "time": slot["time"],
            "platform": platform,
            "character": char_id,
            "type": slot["type"],
            "scenario": slot.get("scenario"),
            "caption": caption_data["caption"],
            "hashtags": caption_data["hashtags"],
            "cta": caption_data["cta"],
            "note": slot.get("note", ""),
        }
        packages.append(pkg)

    # JSON paket
    pkg_path = os.path.join(package_dir, "today_package.json")
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(packages, f, ensure_ascii=False, indent=2)

    # Kopyala-yapıştır dosyası
    txt_path = os.path.join(package_dir, "today_captions.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"📅 {GUN_ISIMLERI[weekday]} {today.strftime('%d/%m/%Y')}\n")
        f.write(f"🎯 {day_plan['theme']}\n")
        f.write(f"{'=' * 50}\n\n")

        for pkg in packages:
            f.write(f"⏰ {pkg['time']} | {pkg['platform'].upper()} | {pkg['character'].upper()}\n")
            f.write(f"📝 {pkg['type']}")
            if pkg.get("scenario"):
                f.write(f" (senaryo: {pkg['scenario']})")
            f.write(f"\n{'─' * 40}\n")
            f.write(f"{pkg['caption']}\n\n")

    print(f"\n✅ Bugünün paketi hazır!")
    print(f"📋 JSON: {pkg_path}")
    print(f"📝 Captions: {txt_path}")
    print(f"📦 {len(packages)} post paketlendi.\n")

    return packages


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AILoverBot Content Calendar")
    parser.add_argument("--generate-week", action="store_true", help="Haftalık takvim JSON üret")
    parser.add_argument("--show-today", action="store_true", help="Bugünün planını göster")
    parser.add_argument("--show-week", action="store_true", help="Haftalık özet göster")
    parser.add_argument("--package-today", action="store_true", help="Bugünün paketini hazırla")

    args = parser.parse_args()

    if args.generate_week:
        generate_week_calendar()
    elif args.show_today:
        show_today()
    elif args.show_week:
        show_week()
    elif args.package_today:
        package_today()
    else:
        # Default: haftalık özet göster
        show_week()


if __name__ == "__main__":
    main()
