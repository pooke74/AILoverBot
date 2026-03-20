# ============================================================
# SOCIAL BATCH GENERATOR
# Tüm karakterler × tüm içerik türleri toplu üretim
# Kullanım:
#   python social_batch_generator.py --week
#   python social_batch_generator.py --type static_post --all-chars
#   python social_batch_generator.py --character mia --type all
#   python social_batch_generator.py --dry-run
# ============================================================

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from post_templates import get_all_characters, CHARACTER_TAGLINES
from caption_engine import generate_caption

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BOT_DIR, "social_output")

# ============================================================
# HAFTALIK İÇERİK PLANI
# ============================================================

WEEKLY_PLAN = {
    0: {  # Pazartesi
        "theme": "Romantik Başlangıç",
        "posts": [
            {"character": "mia", "type": "chat_video", "platform": "tiktok", "scenario": "gece_mesaji"},
            {"character": "mia", "type": "static_post", "platform": "instagram"},
            {"character": "elif", "type": "notification", "platform": "tiktok"},
        ]
    },
    1: {  # Salı
        "theme": "Anime & Lüks",
        "posts": [
            {"character": "yuki", "type": "showcase_video", "platform": "tiktok"},
            {"character": "yuki", "type": "static_post", "platform": "instagram"},
            {"character": "defne", "type": "chat_video", "platform": "tiktok", "scenario": "havuz"},
        ]
    },
    2: {  # Çarşamba
        "theme": "Egzotik & Gizem",
        "posts": [
            {"character": "natasha", "type": "chat_video", "platform": "tiktok", "scenario": "soguk_sicak"},
            {"character": "natasha", "type": "static_post", "platform": "instagram"},
            {"character": "selin", "type": "notification", "platform": "tiktok"},
        ]
    },
    3: {  # Perşembe
        "theme": "Dönüşüm & Tecrübe",
        "posts": [
            {"character": "selin", "type": "chat_video", "platform": "tiktok", "scenario": "ofis_gizli"},
            {"character": "aylin", "type": "showcase_video", "platform": "tiktok"},
            {"character": "aylin", "type": "static_post", "platform": "instagram"},
        ]
    },
    4: {  # Cuma
        "theme": "Masumiyet & Keşif",
        "posts": [
            {"character": "zeynep", "type": "chat_video", "platform": "tiktok", "scenario": "yurt_yalniz"},
            {"character": "zeynep", "type": "static_post", "platform": "instagram"},
            {"character": "mia", "type": "notification", "platform": "tiktok"},
        ]
    },
    5: {  # Cumartesi
        "theme": "VIP Katalog",
        "posts": [
            {"character": "elif", "type": "chat_video", "platform": "tiktok", "scenario": "itaat"},
            {"character": "defne", "type": "static_post", "platform": "instagram"},
            {"character": "yuki", "type": "notification", "platform": "tiktok"},
        ]
    },
    6: {  # Pazar
        "theme": "Engagement Günü",
        "posts": [
            {"character": "mia", "type": "showcase_video", "platform": "tiktok"},
            {"character": "elif", "type": "static_post", "platform": "instagram"},
            {"character": "defne", "type": "notification", "platform": "tiktok"},
        ]
    },
}

GUN_ISIMLERI = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# ============================================================
# BATCH ÜRETİM
# ============================================================

def generate_batch(content_type=None, characters=None, platforms=None, dry_run=False):
    """Toplu içerik üretimi yapar."""
    if characters is None:
        characters = get_all_characters()

    types = [content_type] if content_type and content_type != "all" else [
        "static_post", "notification", "showcase_video"
    ]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    batch_dir = os.path.join(OUTPUT_DIR, f"batch_{timestamp}")
    manifest = {
        "batch_id": timestamp,
        "generated_at": datetime.now().isoformat(),
        "items": [],
    }

    total = len(characters) * len(types)
    current = 0

    print(f"\n{'=' * 60}")
    print(f"  🚀 Batch Content Generator")
    print(f"  Karakterler: {', '.join(c.upper() for c in characters)}")
    print(f"  İçerik Türleri: {', '.join(types)}")
    print(f"  Toplam: {total} içerik")
    print(f"  Çıktı: {batch_dir}")
    print(f"{'=' * 60}")

    if dry_run:
        print("\n⚠️  DRY RUN — Dosya üretilmeyecek, sadece plan gösterilecek.\n")

    for char_id in characters:
        char_dir = os.path.join(batch_dir, char_id)
        if not dry_run:
            os.makedirs(char_dir, exist_ok=True)

        for ctype in types:
            current += 1
            progress = f"[{current}/{total}]"

            # Caption üret
            platform = "tiktok"  # Default
            caption_data = generate_caption(char_id, platform)

            item = {
                "character": char_id,
                "type": ctype,
                "caption": caption_data["caption"],
                "hashtags": caption_data["hashtags"],
                "cta": caption_data["cta"],
                "hook": caption_data["hook"],
                "file": None,
            }

            if dry_run:
                print(f"  {progress} 📋 {char_id.upper()} / {ctype}")
                print(f"         Hook: {caption_data['char_hook']}")
                print(f"         CTA: {caption_data['cta']}")
                manifest["items"].append(item)
                continue

            # Gerçek üretim
            output_path = None
            try:
                if ctype == "static_post":
                    from generate_social_post import generate_static_post
                    output_path = generate_static_post(char_id, size="portrait")

                elif ctype == "notification":
                    from generate_social_post import generate_notification_mockup
                    output_path = generate_notification_mockup(char_id)

                elif ctype == "showcase_video":
                    from generate_social_post import generate_showcase_video
                    output_path = generate_showcase_video(char_id)

                elif ctype == "chat_video":
                    from generate_social_post import generate_chat_video
                    output_path = generate_chat_video(char_id)

                if output_path and os.path.exists(output_path):
                    # Dosyayı batch klasörüne kopyala
                    import shutil
                    dest = os.path.join(char_dir, os.path.basename(output_path))
                    shutil.copy2(output_path, dest)
                    item["file"] = dest
                    print(f"  {progress} ✅ {char_id.upper()} / {ctype} → {os.path.basename(dest)}")
                else:
                    print(f"  {progress} ⚠️  {char_id.upper()} / {ctype} — Üretim başarısız")

            except Exception as e:
                print(f"  {progress} ❌ {char_id.upper()} / {ctype} — Hata: {e}")

            manifest["items"].append(item)

    # Caption dosyası oluştur
    if not dry_run:
        os.makedirs(batch_dir, exist_ok=True)

        # Manifest kaydet
        manifest_path = os.path.join(batch_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Kopyala-yapıştır dosyası
        captions_path = os.path.join(batch_dir, "captions_ready.txt")
        with open(captions_path, "w", encoding="utf-8") as f:
            for item in manifest["items"]:
                f.write(f"{'=' * 50}\n")
                f.write(f"📝 {item['character'].upper()} | {item['type']}\n")
                f.write(f"{'=' * 50}\n")
                f.write(f"{item['caption']}\n\n")

        print(f"\n📋 Manifest: {manifest_path}")
        print(f"📝 Captions: {captions_path}")

    print(f"\n🎉 Batch tamamlandı! {current} içerik {'planlandı' if dry_run else 'üretildi'}.")
    return manifest


def generate_weekly_batch(dry_run=False):
    """Haftalık içerik planını üretir."""
    today = datetime.now()
    weekday = today.weekday()  # 0=Pazartesi

    print(f"\n{'=' * 60}")
    print(f"  📅 Haftalık İçerik Planı")
    print(f"  Başlangıç: {today.strftime('%d/%m/%Y %A')}")
    print(f"{'=' * 60}")

    all_items = []

    for day_offset in range(7):
        day_num = (weekday + day_offset) % 7
        day_plan = WEEKLY_PLAN.get(day_num, {"theme": "Serbest", "posts": []})
        day_date = today + timedelta(days=day_offset)

        gun_ismi = GUN_ISIMLERI[day_num]
        print(f"\n📌 {gun_ismi} ({day_date.strftime('%d/%m')}) — {day_plan['theme']}")
        print("-" * 40)

        for post in day_plan["posts"]:
            char_id = post["character"]
            ctype = post["type"]
            platform = post.get("platform", "tiktok")

            caption_data = generate_caption(char_id, platform)

            item = {
                "day": gun_ismi,
                "date": day_date.strftime("%Y-%m-%d"),
                "character": char_id,
                "type": ctype,
                "platform": platform,
                "scenario": post.get("scenario"),
                "caption": caption_data["caption"],
                "hashtags": caption_data["hashtags"],
                "hook": caption_data["hook"],
            }
            all_items.append(item)

            emoji_map = {
                "chat_video": "🎬",
                "static_post": "📸",
                "showcase_video": "💎",
                "notification": "🔔",
            }
            emoji = emoji_map.get(ctype, "📋")
            print(f"  {emoji} {char_id.upper()} → {ctype} ({platform})")

    # Kaydet
    week_dir = os.path.join(OUTPUT_DIR, f"week_{today.strftime('%Y%m%d')}")
    os.makedirs(week_dir, exist_ok=True)

    plan_path = os.path.join(week_dir, "weekly_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    # Kopyala-yapıştır dosyası
    captions_path = os.path.join(week_dir, "weekly_captions.txt")
    with open(captions_path, "w", encoding="utf-8") as f:
        current_day = ""
        for item in all_items:
            if item["day"] != current_day:
                current_day = item["day"]
                f.write(f"\n{'=' * 50}\n")
                f.write(f"📅 {current_day} ({item['date']})\n")
                f.write(f"{'=' * 50}\n\n")
            f.write(f"📝 {item['character'].upper()} | {item['type']} | {item['platform']}\n")
            f.write(f"{'-' * 40}\n")
            f.write(f"{item['caption']}\n\n")

    print(f"\n📋 Plan: {plan_path}")
    print(f"📝 Captions: {captions_path}")
    print(f"\n✅ 7 günlük plan hazır! {len(all_items)} post planlandı.")

    return all_items


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="AILoverBot Social Batch Generator")
    parser.add_argument("--type", default="all",
                        choices=["chat_video", "static_post", "showcase_video", "notification", "all"],
                        help="Üretilecek içerik türü")
    parser.add_argument("--character", default=None, help="Karakter ID")
    parser.add_argument("--all-chars", action="store_true", help="Tüm karakterler")
    parser.add_argument("--week", action="store_true", help="Haftalık plan üret")
    parser.add_argument("--dry-run", action="store_true", help="Sadece planı göster, üretme")

    args = parser.parse_args()

    if args.week:
        generate_weekly_batch(dry_run=args.dry_run)
    else:
        characters = get_all_characters() if args.all_chars else (
            [args.character] if args.character else ["mia"]
        )
        generate_batch(
            content_type=args.type,
            characters=characters,
            dry_run=args.dry_run,
        )


if __name__ == "__main__":
    main()
