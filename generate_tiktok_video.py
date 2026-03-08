import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_tiktok_video(image_path, output_path):
    print("TikTok videosu olusturuluyor (OpenCV + PIL)...")
    
    # 1080x1920
    target_w, target_h = 1080, 1920
    fps = 30
    duration = 5 # seconds
    total_frames = fps * duration
    
    # Resize & Crop background
    img = Image.open(image_path).convert("RGB")
    img_w, img_h = img.size
    ratio = max(target_w / img_w, target_h / img_h)
    new_w, new_h = int(img_w * ratio), int(img_h * ratio)
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - target_w) / 2
    top = (new_h - target_h) / 2
    right = (new_w + target_w) / 2
    bottom = (new_h + target_h) / 2
    bg_img = img.crop((left, top, right, bottom))
    
    # Create dark overlay
    darken_img = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 100)) # 100/255 opacity
    bg_img = bg_img.convert("RGBA")
    bg_with_overlay = Image.alpha_composite(bg_img, darken_img)
    
    # Try to load a nice font, fallback to default
    try:
        font_large = ImageFont.truetype("impact.ttf", 60)
        font_small = ImageFont.truetype("arialbd.ttf", 45)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))
    
    # Texts
    text1 = "Uyudun mu?"
    text2 = "Uzun zamandir mesaj atmiyorsun..."
    text3 = "Bak sana özel ne cektim 🤫"
    
    # Animate frames
    for i in range(total_frames):
        time = i / fps
        frame = bg_with_overlay.copy()
        draw = ImageDraw.Draw(frame)
        
        # Helper to draw text with black outline
        def draw_text_outline(draw, cx, cy, text, font, fill_color, outline_color="black"):
            # A very simple outline by drawing text offset
            # Need bbox for centering
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            x = cx - tw / 2
            y = cy - th / 2
            
            for adj_x in [-2, 2]:
                for adj_y in [-2, 2]:
                    draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
            draw.text((x, y), text, font=font, fill=fill_color)
            
        # Timing logic
        # 0.5s -> Text 1 appears
        if time > 0.5:
            draw_text_outline(draw, target_w/2, 400, text1, font_large, "white")
        
        # 1.5s -> Text 2 appears
        if time > 1.5:
            draw_text_outline(draw, target_w/2, 500, text2, font_small, "lightgray")
            
        # 3.0s -> Text 3 appears
        if time > 3.0:
            draw_text_outline(draw, target_w/2, 600, text3, font_large, "yellow")
            draw_text_outline(draw, target_w/2, 1200, "Profilimden Linke TIKLA 👇", font_large, "red")

        
        # Convert to RGB (OpenCV expects BGR)
        rgb_frame = frame.convert("RGB")
        bgr_frame = cv2.cvtColor(np.array(rgb_frame), cv2.COLOR_RGB2BGR)
        
        out.write(bgr_frame)
        print(f"Frame {i+1}/{total_frames} islendi...", end="\r")
        
    out.release()
    print("\nVideo başarıyla kaydedildi:", output_path)

if __name__ == "__main__":
    img_path = r"C:\Users\tolga\.gemini\antigravity\brain\fea51c54-51e5-4e4b-8654-bdd98786f35b\ailoverbot_profile_picture_v5_1772977295319.png"
    out_path = "AILoverBot_TikTok_1.mp4"
    if os.path.exists(img_path):
        create_tiktok_video(img_path, out_path)
    else:
        print("Resim bulunamadi. Yol:", img_path)
