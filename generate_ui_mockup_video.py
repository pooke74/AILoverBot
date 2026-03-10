import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import math

def draw_rounded_rectangle(draw, xy, cornerradius, fill):
    upper_left_point = xy[0]
    bottom_right_point = xy[1]
    draw.rectangle(
        [
            (upper_left_point[0], upper_left_point[1] + cornerradius),
            (bottom_right_point[0], bottom_right_point[1] - cornerradius)
        ],
        fill=fill,
    )
    draw.rectangle(
        [
            (upper_left_point[0] + cornerradius, upper_left_point[1]),
            (bottom_right_point[0] - cornerradius, bottom_right_point[1])
        ],
        fill=fill,
    )
    draw.pieslice([upper_left_point[0], upper_left_point[1], upper_left_point[0] + cornerradius * 2, upper_left_point[1] + cornerradius * 2], 180, 270, fill=fill)
    draw.pieslice([bottom_right_point[0] - cornerradius * 2, bottom_right_point[1] - cornerradius * 2, bottom_right_point[0], bottom_right_point[1]], 0, 90, fill=fill)
    draw.pieslice([upper_left_point[0], bottom_right_point[1] - cornerradius * 2, upper_left_point[0] + cornerradius * 2, bottom_right_point[1]], 90, 180, fill=fill)
    draw.pieslice([bottom_right_point[0] - cornerradius * 2, upper_left_point[1], bottom_right_point[0], upper_left_point[1] + cornerradius * 2], 270, 360, fill=fill)

def get_circular_avatar(img, size=100):
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img

def create_ios_notification(draw, y_offset, icon_img, title, message, font_title, font_msg, width=1000):
    # Base Box
    box_x1 = 40
    box_y1 = y_offset
    box_x2 = box_x1 + width
    box_y2 = box_y1 + 160
    
    # Frosty glass effect base
    draw_rounded_rectangle(draw, [(box_x1, box_y1), (box_x2, box_y2)], 40, (230, 230, 230, 220))
    
    # Text
    draw.text((box_x1 + 160, box_y1 + 35), title, font=font_title, fill=(30, 30, 30, 255))
    draw.text((box_x1 + 160, box_y1 + 90), message, font=font_msg, fill=(70, 70, 70, 255))
    
    # Add Telegram Header text
    try:
        font_small = ImageFont.truetype("arial.ttf", 25)
    except:
        font_small = ImageFont.load_default()
    draw.text((box_x1 + 160, box_y1 + 10), "TELEGRAM", font=font_small, fill=(100, 100, 100, 255))
    draw.text((box_x2 - 100, box_y1 + 15), "now", font=font_small, fill=(100, 100, 100, 255))

def get_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("arialbd.ttf", size)
        else:
            return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()

def create_ui_fake_video(bg_path, output_path):
    print("iOS Telegram Simülasyonu olusturuluyor...")
    target_w, target_h = 1080, 1920
    fps = 30
    duration = 10 # 10 saniye
    total_frames = fps * duration

    # 1. Background image processing
    if not os.path.exists(bg_path):
        bg_img = Image.new('RGB', (target_w, target_h), color=(30, 30, 30))
    else:
        bg_img = Image.open(bg_path).convert("RGB")
    
    # Crop and blur background
    img_w, img_h = bg_img.size
    ratio = max(target_w / img_w, target_h / img_h)
    new_w, new_h = int(img_w * ratio), int(img_h * ratio)
    bg_img = bg_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - target_w) / 2
    top = (new_h - target_h) / 2
    right = (new_w + target_w) / 2
    bottom = (new_h + target_h) / 2
    bg_img = bg_img.crop((left, top, right, bottom))
    
    # Blur the background like a lock screen
    bg_cv = cv2.cvtColor(np.array(bg_img), cv2.COLOR_RGB2BGR)
    bg_cv = cv2.GaussianBlur(bg_cv, (35, 35), 0)
    bg_img = Image.fromarray(cv2.cvtColor(bg_cv, cv2.COLOR_BGR2RGBA))

    # Avatar
    avatar_img = get_circular_avatar(Image.open(bg_path).crop((left, top, right, top+target_w)), 100) if os.path.exists(bg_path) else None

    # Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))
    
    font_title = get_font(40, bold=True)
    font_msg = get_font(35, bold=False)
    
    notifications = [
        {"time": 1.0, "title": "Mia 🌸", "msg": "Uyudun mu? 🥺"},
        {"time": 3.0, "title": "Mia 🌸", "msg": "Tum gun yazmani bekledim..."},
        {"time": 5.0, "title": "Mia 🌸", "msg": "📷 Photo (Self-destructing)"},
        {"time": 7.0, "title": "Mia 🌸", "msg": "Buna ne kadar dayanabileceksin gorelim 🤫"}
    ]

    def ease_out(t):
        return 1 - math.pow(1 - t, 3)

    for i in range(total_frames):
        t = i / fps
        frame = bg_img.copy()
        draw = ImageDraw.Draw(frame)
        
        # Draw Clock
        draw.text((target_w/2 - 140, 150), "02:14", font=get_font(120, bold=True), fill=(255, 255, 255, 255))
        draw.text((target_w/2 - 120, 280), "Sunday, October 24", font=get_font(30), fill=(255, 255, 255, 255))

        # Render notifications
        current_y = 400
        for notif in notifications:
            if t >= notif["time"]:
                age = t - notif["time"]
                
                # Drop down animation
                anim_dur = 0.5
                if age < anim_dur:
                    prog = age / anim_dur
                    y_pos = current_y - 50 * (1 - ease_out(prog))
                    alpha = int(255 * ease_out(prog))
                else:
                    y_pos = current_y
                    alpha = 255
                    
                # Create a temporary transparent image for alpha blending the notification
                notif_layer = Image.new('RGBA', (target_w, target_h), (0,0,0,0))
                ndraw = ImageDraw.Draw(notif_layer)
                
                create_ios_notification(ndraw, y_pos, None, notif["title"], notif["msg"], font_title, font_msg, width=1000)
                if avatar_img:
                    notif_layer.paste(avatar_img, (70, int(y_pos) + 35), avatar_img)
                
                # Apply alpha
                if alpha < 255:
                    notif_layer.putalpha(notif_layer.split()[3].point(lambda p: p * (alpha/255.0)))
                    
                frame = Image.alpha_composite(frame, notif_layer)
                current_y += 180 # spacing

        # Draw "Swipe up to open"
        draw.text((target_w/2 - 100, target_h - 100), "Swipe up to open", font=get_font(30), fill=(200, 200, 200, 255))
        draw.rectangle([(target_w/2 - 150, target_h - 40), (target_w/2 + 150, target_h - 30)], fill=(255, 255, 255, 255))

        # Output
        rgb_frame = frame.convert("RGB")
        bgr_frame = cv2.cvtColor(np.array(rgb_frame), cv2.COLOR_RGB2BGR)
        out.write(bgr_frame)

    out.release()
    print(f"Bitti: {output_path}")

if __name__ == "__main__":
    base_dir = r"C:\Users\tolga\.gemini\antigravity\brain\fea51c54-51e5-4e4b-8654-bdd98786f35b"
    mia_img = os.path.join(base_dir, "ig_post_1_morning_generic_1773004935645.png")
    out_path = "AILoverBot_Telegram_Sizinti.mp4"
    create_ui_fake_video(mia_img, out_path)
