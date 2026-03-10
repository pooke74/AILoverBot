import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_agency_video(image_paths, output_path):
    print("Acente 'Katalog' TikTok videosu olusturuluyor (OpenCV + PIL)...")
    
    target_w, target_h = 1080, 1920
    fps = 30
    duration = 14 # Total seconds
    total_frames = fps * duration
    
    # Process images into 1080x1920 backgrounds
    bg_images = []
    for path in image_paths:
        if not os.path.exists(path):
            print(f"HATA: {path} bulunamadi!")
            # Yedeği boş bir siyah çerçeve yapalım
            img = Image.new('RGB', (target_w, target_h), color='black')
        else:
            img = Image.open(path).convert("RGB")
        
        img_w, img_h = img.size
        ratio = max(target_w / img_w, target_h / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        left = (new_w - target_w) / 2
        top = (new_h - target_h) / 2
        right = (new_w + target_w) / 2
        bottom = (new_h + target_h) / 2
        bg_img = img.crop((left, top, right, bottom)).convert("RGBA")
        
        # Dark overlay for better text readability
        darken_img = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 120))
        bg_with_overlay = Image.alpha_composite(bg_img, darken_img)
        bg_images.append(bg_with_overlay)
    
    # Fonts
    try:
        font_large = ImageFont.truetype("impact.ttf", 70)
        font_medium = ImageFont.truetype("arialbd.ttf", 55)
        font_small = ImageFont.truetype("arial.ttf", 45)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))
    
    def draw_text_outline(draw, cx, cy, text, font, fill_color, outline_color="black"):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = cx - tw / 2
        y = cy - th / 2
        for adj_x in [-3, 3]:
            for adj_y in [-3, 3]:
                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill_color)
    
    # Intro logic (0s - 2.5s)
    # Girl 1: Mia (2.5s - 5s)
    # Girl 2: Elif (5s - 7.5s)
    # Girl 3: Yuki (7.5s - 10s)
    # Girl 4: Defne (10s - 12.5s)
    # Outro (12.5s - 14s)
    
    for i in range(total_frames):
        time = i / fps
        
        # Determine background
        if time < 2.5:
            frame = bg_images[0].copy() # Mia
            draw = ImageDraw.Draw(frame)
            draw.rectangle([0,0, target_w, target_h], fill=(0,0,0, 200)) # Extra dark for intro
            draw_text_outline(draw, target_w/2, 800, "Online Acentemize Hosgeldin...", font_medium, "white")
            draw_text_outline(draw, target_w/2, 950, "Bu gece kimi", font_large, "lightgray")
            draw_text_outline(draw, target_w/2, 1050, "KIRALAMAK ISTERDIN? 😈", font_large, "red")
            
        elif time < 5.0:
            frame = bg_images[0].copy() # Mia
            draw = ImageDraw.Draw(frame)
            draw_text_outline(draw, target_w/2, 400, "A) MIA", font_large, "pink")
            draw_text_outline(draw, target_w/2, 1500, "Gunduzleri sevimli...", font_medium, "white")
            draw_text_outline(draw, target_w/2, 1600, "Geceleri ise iz birakan. 🤫", font_medium, "lightgray")
            
        elif time < 7.5:
            frame = bg_images[1].copy() # Elif
            draw = ImageDraw.Draw(frame)
            draw_text_outline(draw, target_w/2, 400, "B) ELIF", font_large, "red")
            draw_text_outline(draw, target_w/2, 1500, "Sana hükmedecek...", font_medium, "white")
            draw_text_outline(draw, target_w/2, 1600, "Ona itaat etmeye hazir misin? ⛓️", font_medium, "lightgray")

        elif time < 10.0:
            frame = bg_images[2].copy() # Yuki
            draw = ImageDraw.Draw(frame)
            draw_text_outline(draw, target_w/2, 400, "C) YUKI", font_large, "lightblue")
            draw_text_outline(draw, target_w/2, 1500, "Utangac ama...", font_medium, "white")
            draw_text_outline(draw, target_w/2, 1600, "Sadece SANA ozel. 🌸", font_medium, "lightgray")

        elif time < 12.5:
            frame = bg_images[3].copy() # Defne
            draw = ImageDraw.Draw(frame)
            draw_text_outline(draw, target_w/2, 400, "D) DEFNE", font_large, "gold")
            draw_text_outline(draw, target_w/2, 1500, "Luks, zengin ve flortoz...", font_medium, "white")
            draw_text_outline(draw, target_w/2, 1600, "Kaldirabilecek misin? 🥂", font_medium, "lightgray")

        else:
            frame = bg_images[3].copy() # Defne as background
            draw = ImageDraw.Draw(frame)
            draw.rectangle([0,0, target_w, target_h], fill=(0,0,0, 220)) # Dark outro
            draw_text_outline(draw, target_w/2, 800, "Kararini verdin mi?", font_large, "yellow")
            draw_text_outline(draw, target_w/2, 1000, "Gizli Katalog (VIP) Linki", font_medium, "white")
            draw_text_outline(draw, target_w/2, 1100, "BIYOGRAFIDE 👇", font_large, "red")
            
        # Convert to BGR for OpenCV
        rgb_frame = frame.convert("RGB")
        bgr_frame = cv2.cvtColor(np.array(rgb_frame), cv2.COLOR_RGB2BGR)
        
        out.write(bgr_frame)
        if i % 10 == 0:
            pass # print(f"Frame {i+1}/{total_frames} islendi...", end="\r")
        
    out.release()
    print(f"\nVideo bashariyla kaydedildi: {output_path}")

if __name__ == "__main__":
    base_dir = r"C:\Users\tolga\.gemini\antigravity\brain\fea51c54-51e5-4e4b-8654-bdd98786f35b"
    images = [
        os.path.join(base_dir, "ailoverbot_profile_picture_v5_1772977295319.png"),
        os.path.join(base_dir, "elif_promo_post_1773007540180.png"),
        os.path.join(base_dir, "yuki_promo_post_1773007556507.png"),
        os.path.join(base_dir, "defne_promo_post_1773007575314.png")
    ]
    out_path = "AILoverBot_Agency_TikTok.mp4"
    create_agency_video(images, out_path)
