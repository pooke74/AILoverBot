# ============================================================
# SOSYAL MEDYA POST GENERATOR
# TikTok & Instagram icin otomatik icerik uretici
# Kullanim:
#   python generate_social_post.py --type chat_video --character mia
#   python generate_social_post.py --type static_post --character elif
#   python generate_social_post.py --type all --character defne
# ============================================================

import argparse
import json
import os
import sys
import time

# Windows encoding fix
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import urllib.parse
import http.server
import threading

# --- Pillow & OpenCV ---
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np

# --- Local ---
from post_templates import (
    CHAT_SCENARIOS,
    CHARACTER_TAGLINES,
    get_hashtags,
    get_random_scenario,
    get_random_caption,
    get_all_characters,
)

BOT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BOT_DIR, "social_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# FONTS
# ============================================================
def _load_font(name, size, fallback_name="arial.ttf"):
    try:
        return ImageFont.truetype(name, size)
    except Exception:
        try:
            return ImageFont.truetype(fallback_name, size)
        except Exception:
            return ImageFont.load_default()


FONT_TITLE = _load_font("georgiab.ttf", 62)
FONT_SUBTITLE = _load_font("georgia.ttf", 42)
FONT_SMALL = _load_font("arial.ttf", 32)
FONT_CTA = _load_font("arialbd.ttf", 36)
FONT_HASHTAG = _load_font("arial.ttf", 24)

GOLD = (212, 175, 55)
WHITE = (255, 255, 255)
OFF_WHITE = (220, 220, 220)

# ============================================================
# 1. CHAT VIDEO (Telegram sohbet simulasyonu)
# ============================================================
def generate_chat_video(character_id: str, scenario_name: str = None):
    """Telegram sohbet simulasyonu videosu uretir."""
    print(f"\n🎬 Chat Video uretiliyor: {character_id}")

    scenarios = CHAT_SCENARIOS.get(character_id, CHAT_SCENARIOS["mia"])
    if scenario_name:
        scenario = next((s for s in scenarios if s["name"] == scenario_name), scenarios[0])
    else:
        import random
        scenario = random.choice(scenarios)

    print(f"   Senaryo: {scenario['name']}")

    # Sohbet verisini JSON olarak encode et
    conv_json = json.dumps(scenario["conversation"], ensure_ascii=False)
    encoded = urllib.parse.quote(conv_json)

    # Toplam sureyi hesapla
    total_delay_ms = sum(m.get("delay", 1000) for m in scenario["conversation"])
    # Typing animation sureleri ekle
    for m in scenario["conversation"]:
        if m["type"].startswith("incoming") and m.get("text"):
            total_delay_ms += min(len(m["text"]) * 40, 2500)
    # Basa 1.2s + sona 3s ekle
    total_delay_ms += 1200 + 3000
    duration = int(total_delay_ms / 1000) + 2

    html_file = "telegram_chat_sim_dynamic.html"
    url = f"http://127.0.0.1:8765/{html_file}?character={character_id}&scenario={encoded}&clock=02:14"

    output_path = os.path.join(OUTPUT_DIR, f"chat_{character_id}_{scenario['name']}.mp4")
    _record_browser_video(url, output_path, duration=duration)
    return output_path


def _start_server(port=8765, directory="."):
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=directory, **kwargs
    )
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def _record_browser_video(url, output_path, duration=30, fps=15):
    """Selenium ile browser'i kaydeder."""
    print(f"   Selenium kaydı başlıyor ({duration}s)...")

    httpd = _start_server(port=8765, directory=BOT_DIR)
    time.sleep(1)

    # Chrome veya Edge dene
    driver = None
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=420,900")
        chrome_options.add_argument("--force-device-scale-factor=2")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--hide-scrollbars")

        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception:
            from selenium.webdriver.edge.options import Options as EdgeOptions

            edge_options = EdgeOptions()
            for arg in [
                "--headless=new", "--window-size=420,900",
                "--force-device-scale-factor=2", "--disable-gpu",
                "--no-sandbox", "--hide-scrollbars",
            ]:
                edge_options.add_argument(arg)
            driver = webdriver.Edge(options=edge_options)

        driver.get(url)
        time.sleep(2)

        # Screenshot boyutlari
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(__import__("io").BytesIO(screenshot))
        w, h = img.size

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        total_frames = int(duration * fps)
        interval = 1.0 / fps
        start_time = time.time()

        for i in range(total_frames):
            target_time = start_time + (i * interval)
            screenshot = driver.get_screenshot_as_png()
            img = Image.open(__import__("io").BytesIO(screenshot))
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            out.write(frame)

            now = time.time()
            sleep_time = target_time - now
            if sleep_time > 0:
                time.sleep(sleep_time)

            if i % (fps * 5) == 0:
                elapsed = time.time() - start_time
                print(f"   Kare {i}/{total_frames} ({elapsed:.1f}s)")

        out.release()
        driver.quit()
        httpd.shutdown()
        print(f"   ✅ Chat video kaydedildi: {output_path}")

    except ImportError:
        print("   ❌ Selenium yuklu degil! pip install selenium")
        if httpd:
            httpd.shutdown()
        return None
    except Exception as e:
        print(f"   ❌ Hata: {e}")
        if driver:
            driver.quit()
        httpd.shutdown()
        return None

    return output_path


# ============================================================
# 2. STATIC POST (Instagram Feed - Karakter Tanitim Gorseli)
# ============================================================
def generate_static_post(character_id: str, size="portrait"):
    """Statik Instagram postu uretir (karakter portre + tagline)."""
    print(f"\n📸 Statik post uretiliyor: {character_id}")

    # Boyut
    if size == "square":
        w, h = 1080, 1080
    else:  # portrait
        w, h = 1080, 1350

    # Karakter referans gorseli
    ref_path = os.path.join(BOT_DIR, "character_refs", f"{character_id}_ref.png")
    if not os.path.exists(ref_path):
        print(f"   ❌ Referans gorsel bulunamadi: {ref_path}")
        return None

    # Gorseli yukle ve boyutlandir
    img = Image.open(ref_path).convert("RGBA")
    img_w, img_h = img.size
    ratio = max(w / img_w, h / img_h)
    img = img.resize((int(img_w * ratio), int(img_h * ratio)), Image.Resampling.LANCZOS)

    # Ortala ve kirp
    img_w, img_h = img.size
    left = (img_w - w) // 2
    top = (img_h - h) // 2
    img = img.crop((left, top, left + w, top + h))

    # Gradient overlay (alt kisim koyu)
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_g = ImageDraw.Draw(gradient)
    for y in range(h):
        alpha = 0
        if y > h * 0.4:
            progress = (y - h * 0.4) / (h * 0.6)
            alpha = int(220 * progress)
        draw_g.rectangle([0, y, w, y + 1], fill=(0, 0, 0, alpha))

    frame = Image.alpha_composite(img, gradient)
    draw = ImageDraw.Draw(frame)

    # Tagline bilgileri
    info = CHARACTER_TAGLINES.get(character_id, CHARACTER_TAGLINES["mia"])
    tagline = info["tagline"]
    short_tag = info["short_tagline"]

    # Ust kisim: kucuk tagline
    _draw_centered_text(draw, short_tag, 60, FONT_SMALL, (*GOLD, 230), w)

    # Alt kisim: ana tagline
    _draw_centered_text(draw, tagline, h - 220, FONT_SUBTITLE, (*WHITE, 255), w, shadow=True)

    # CTA
    _draw_centered_text(draw, "Bio'daki linke tıkla 👆", h - 130, FONT_CTA, (*GOLD, 255), w, shadow=True)

    # Hashtag
    hashtags = get_hashtags(character_id, limit=8)
    _draw_centered_text(draw, hashtags, h - 70, FONT_HASHTAG, (*OFF_WHITE, 180), w)

    # Kaydet
    output_path = os.path.join(OUTPUT_DIR, f"post_{character_id}_{size}.png")
    frame.convert("RGB").save(output_path, quality=95)
    print(f"   ✅ Statik post kaydedildi: {output_path}")
    return output_path


def _draw_centered_text(draw, text, y, font, color, canvas_w, shadow=False):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (canvas_w - tw) // 2
    if shadow:
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, int(color[3] * 0.7)))
    draw.text((x, y), text, font=font, fill=color)


# ============================================================
# 3. CHARACTER SHOWCASE VIDEO (Ken Burns - Pro Tanitim)
# ============================================================
def generate_showcase_video(character_id: str):
    """Ken Burns efektli karakter tanitim videosu uretir."""
    print(f"\n💎 Showcase video uretiliyor: {character_id}")

    ref_path = os.path.join(BOT_DIR, "character_refs", f"{character_id}_ref.png")
    if not os.path.exists(ref_path):
        print(f"   ❌ Referans gorsel bulunamadi: {ref_path}")
        return None

    target_w, target_h = 1080, 1920
    fps = 30
    duration = 6
    total_frames = fps * duration

    # Gorseli yukle
    img = Image.open(ref_path).convert("RGB")
    zoom_factor = 1.15
    img_w, img_h = img.size
    ratio = max((target_w * zoom_factor) / img_w, (target_h * zoom_factor) / img_h)
    img = img.resize((int(img_w * ratio), int(img_h * ratio)), Image.Resampling.LANCZOS)

    output_path = os.path.join(OUTPUT_DIR, f"showcase_{character_id}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))

    info = CHARACTER_TAGLINES.get(character_id, CHARACTER_TAGLINES["mia"])

    for i in range(total_frames):
        t = i / fps
        progress = t / duration

        # Ken Burns: zoom & pan
        img_w, img_h = img.size
        cx, cy = img_w / 2, img_h / 2
        pan_y = (img_h - target_h) * progress
        left = cx - target_w / 2
        top = pan_y
        bg = img.crop((left, top, left + target_w, top + target_h)).convert("RGBA")

        # Dark overlay
        overlay = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 100))
        frame = Image.alpha_composite(bg, overlay)

        draw = ImageDraw.Draw(frame)

        # Fade in/out alpha
        alpha = _get_alpha(t, 0, duration, fade_dur=0.8)
        a = int(255 * alpha)

        # Tagline
        _draw_centered_text(draw, info["tagline"], target_h - 450, FONT_TITLE, (*GOLD, a), target_w, shadow=True)
        _draw_centered_text(draw, info["short_tagline"], target_h - 350, FONT_SUBTITLE, (*WHITE, a), target_w, shadow=True)

        # Sinematik siyah barlar
        bar_h = 160
        draw.rectangle([0, 0, target_w, bar_h], fill=(0, 0, 0, 255))
        draw.rectangle([0, target_h - bar_h, target_w, target_h], fill=(0, 0, 0, 255))

        # Convert
        rgb = frame.convert("RGB")
        bgr = cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)
        out.write(bgr)

    out.release()
    print(f"   ✅ Showcase video kaydedildi: {output_path}")
    return output_path


def _get_alpha(time, start, end, fade_dur=0.5):
    if time < start:
        return 0.0
    if time > end:
        return 0.0
    if time < start + fade_dur:
        return (time - start) / fade_dur
    if time > end - fade_dur:
        return (end - time) / fade_dur
    return 1.0


# ============================================================
# 4. NOTIFICATION MOCKUP (Telefon bildirimi)
# ============================================================
def generate_notification_mockup(character_id: str):
    """Telefon bildirimi tarzinda gorsel uretir."""
    print(f"\n🔔 Notification mockup uretiliyor: {character_id}")

    w, h = 1080, 1920
    info = CHARACTER_TAGLINES.get(character_id, CHARACTER_TAGLINES["mia"])

    # Karakter referans gorseli - blurlanmis arka plan
    ref_path = os.path.join(BOT_DIR, "character_refs", f"{character_id}_ref.png")
    if os.path.exists(ref_path):
        bg = Image.open(ref_path).convert("RGB")
        bg_w, bg_h = bg.size
        ratio = max(w / bg_w, h / bg_h)
        bg = bg.resize((int(bg_w * ratio), int(bg_h * ratio)), Image.Resampling.LANCZOS)
        bg_w, bg_h = bg.size
        bg = bg.crop(((bg_w - w) // 2, (bg_h - h) // 2, (bg_w + w) // 2, (bg_h + h) // 2))
        bg = bg.filter(ImageFilter.GaussianBlur(radius=25))
    else:
        bg = Image.new("RGB", (w, h), (15, 22, 33))

    frame = bg.convert("RGBA")

    # Dark overlay
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 160))
    frame = Image.alpha_composite(frame, overlay)
    draw = ImageDraw.Draw(frame)

    # Saat
    _draw_centered_text(draw, "02:14", 300, _load_font("arialbd.ttf", 120), (*WHITE, 255), w)
    _draw_centered_text(draw, "Perşembe, 12 Mart", 440, FONT_SMALL, (*OFF_WHITE, 200), w)

    # Notification card
    card_y = 580
    card_h = 180
    card_margin = 40

    # Rounded rectangle (notification)
    card_rect = [card_margin, card_y, w - card_margin, card_y + card_h]
    draw.rounded_rectangle(card_rect, radius=20, fill=(30, 40, 55, 230))

    # App icon placeholder
    icon_x, icon_y = card_margin + 20, card_y + 20
    draw.rounded_rectangle([icon_x, icon_y, icon_x + 50, icon_y + 50], radius=10, fill=(*GOLD, 255))
    draw.text((icon_x + 12, icon_y + 8), "T", font=_load_font("arialbd.ttf", 30), fill=(0, 0, 0, 255))

    # Notification text
    char_names = {
        "mia": "Mia 🌸", "elif": "Elif 🔥", "yuki": "Yuki 🌙", "defne": "Defne 💋",
        "natasha": "Natasha ❄️", "selin": "Selin 👓", "aylin": "Aylin 🍒", "zeynep": "Zeynep 🎀",
    }
    name = char_names.get(character_id, "Mia 🌸")
    draw.text((icon_x + 65, icon_y + 2), "Telegram", font=_load_font("arial.ttf", 22), fill=(*OFF_WHITE, 180))
    draw.text((icon_x + 65, icon_y + 32), f"{name}", font=_load_font("arialbd.ttf", 28), fill=(*WHITE, 255))

    # Mesaj on izleme
    scenarios = CHAT_SCENARIOS.get(character_id, CHAT_SCENARIOS["mia"])
    first_msg = ""
    for m in scenarios[0]["conversation"]:
        if m["type"] == "incoming" and m.get("text"):
            first_msg = m["text"]
            break
    draw.text(
        (icon_x + 20, card_y + 100),
        first_msg[:45] + ("..." if len(first_msg) > 45 else ""),
        font=_load_font("arial.ttf", 26),
        fill=(*OFF_WHITE, 220),
    )

    # Alt CTA
    _draw_centered_text(draw, "Devamını görmek için kaydır 👆", h - 300, FONT_CTA, (*GOLD, 255), w, shadow=True)

    output_path = os.path.join(OUTPUT_DIR, f"notification_{character_id}.png")
    frame.convert("RGB").save(output_path, quality=95)
    print(f"   ✅ Notification mockup kaydedildi: {output_path}")
    return output_path


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="AILoverBot Sosyal Medya Post Generator")
    parser.add_argument(
        "--type",
        choices=["chat_video", "static_post", "showcase_video", "notification", "all"],
        default="all",
        help="Uretilecek post turu",
    )
    parser.add_argument(
        "--character",
        default="mia",
        help="Karakter ID (mia, elif, yuki, defne, natasha, selin, aylin, zeynep)",
    )
    parser.add_argument("--scenario", default=None, help="Sohbet senaryo adi")
    parser.add_argument("--size", default="portrait", choices=["portrait", "square"], help="Statik post boyutu")
    parser.add_argument("--all-chars", action="store_true", help="Tum karakterler icin uret")

    args = parser.parse_args()

    characters = get_all_characters() if args.all_chars else [args.character]

    for char_id in characters:
        print(f"\n{'='*50}")
        print(f"  Karakter: {char_id.upper()}")
        print(f"{'='*50}")

        if args.type in ("static_post", "all"):
            generate_static_post(char_id, size=args.size)

        if args.type in ("notification", "all"):
            generate_notification_mockup(char_id)

        if args.type in ("showcase_video", "all"):
            generate_showcase_video(char_id)

        if args.type in ("chat_video", "all"):
            generate_chat_video(char_id, scenario_name=args.scenario)

    print(f"\n🎉 Tum ciktilar: {OUTPUT_DIR}")

    # Caption ve hashtag onerileri
    for char_id in characters:
        caption = get_random_caption(char_id)
        hashtags = get_hashtags(char_id)
        print(f"\n📝 {char_id.upper()} Caption Onerisi:")
        print(f"   {caption}")
        print(f"   {hashtags}")


if __name__ == "__main__":
    main()
