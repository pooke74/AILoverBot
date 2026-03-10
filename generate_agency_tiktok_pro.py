import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def create_pro_agency_video(image_paths, output_path):
    print("Profesyonel VIP Acente Katalog videosu olusturuluyor...")
    
    target_w, target_h = 1080, 1920
    fps = 30
    duration = 16 # Longer duration for smoother transitions
    total_frames = fps * duration
    
    # Process images into larger sizes for Ken Burns (zooming) effect
    bg_images = []
    for path in image_paths:
        if not os.path.exists(path):
            img = Image.new('RGB', (target_w, target_h), color='black')
        else:
            img = Image.open(path).convert("RGB")
        
        # Resize to be 15% larger than target for zoom effect
        zoom_factor = 1.15
        img_w, img_h = img.size
        ratio = max((target_w * zoom_factor) / img_w, (target_h * zoom_factor) / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        bg_images.append(img)
        
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # type: ignore
    out = cv2.VideoWriter(output_path, fourcc, fps, (target_w, target_h))
    
    # Elegant Fonts
    try:
        font_title = ImageFont.truetype("georgia.ttf", 65) # Serif for elegance
        font_subtitle = ImageFont.truetype("georgiab.ttf", 50)
        font_small = ImageFont.truetype("arial.ttf", 35)
    except:
        try:
            # Try arial if georgia is not found
            font_title = ImageFont.truetype("arialbd.ttf", 65)
            font_subtitle = ImageFont.truetype("arial.ttf", 50)
            font_small = ImageFont.truetype("arial.ttf", 35)
        except:
            font_title = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
    # Colors
    gold = (212, 175, 55)
    white = (255, 255, 255)
    off_white = (220, 220, 220)
    
    def get_zoomed_crop(img, progress):
        # Center coordinates
        img_w, img_h = img.size
        cx, cy = img_w / 2, img_h / 2
        
        # Pan effect (move crop window down slowly)
        pan_y = (img_h - target_h) * progress
        
        left = cx - target_w / 2
        top = pan_y
        right = cx + target_w / 2
        bottom = pan_y + target_h
        
        return img.crop((left, top, right, bottom)).convert("RGBA")

    def draw_text_elegant(draw, text, y, font, color, center_x=target_w/2, shadow=True):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = center_x - tw / 2
        if shadow:
            # Soft shadow
            draw.text((x+3, y+3), text, font=font, fill=(0,0,0, int(color[3]*0.8)))
        draw.text((x, y), text, font=font, fill=color)

    def get_alpha(time, start, end, fade_dur=0.5):
        if time < start: return 0.0
        if time > end: return 0.0
        if time < start + fade_dur:
            return (time - start) / fade_dur
        if time > end - fade_dur:
            return (end - time) / fade_dur
        return 1.0

    for i in range(total_frames):
        time = i / fps
        
        # Create base frame
        frame = Image.new('RGBA', (target_w, target_h), (0,0,0,255))
        
        # Determine active image and segment progress
        if time < 3.0:
            # Intro - Mia blurred
            prog = time / 3.0
            bg = get_zoomed_crop(bg_images[0], prog)
            # Blur using PIL filter or cv2
            bg_cv = cv2.cvtColor(np.array(bg), cv2.COLOR_RGBA2BGR)
            bg_cv = cv2.GaussianBlur(bg_cv, (45, 45), 0)
            bg = Image.fromarray(cv2.cvtColor(bg_cv, cv2.COLOR_BGR2RGBA))
            
            # Darken overlay
            overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,160))
            frame = Image.alpha_composite(bg, overlay)
            
            draw = ImageDraw.Draw(frame)
            alpha = int(255 * get_alpha(time, 0.0, 3.0, 1.0))
            draw_text_elegant(draw, "THE EXCLUSIVE CLUB", target_h/2 - 100, font_title, (*gold, alpha))
            draw_text_elegant(draw, "Bu Gece Kimi Istiyorsun?", target_h/2 + 20, font_subtitle, (*white, alpha))
            
        elif time < 6.0:
            prog = (time - 3.0) / 3.0
            bg = get_zoomed_crop(bg_images[0], prog)
            
            overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,100))
            frame = Image.alpha_composite(bg, overlay)
            
            draw = ImageDraw.Draw(frame)
            alpha = int(255 * get_alpha(time, 3.0, 6.0))
            draw_text_elegant(draw, "1. M I A", target_h - 450, font_title, (*gold, alpha))
            draw_text_elegant(draw, "Gunduzleri masum...", target_h - 350, font_subtitle, (*white, alpha))
            draw_text_elegant(draw, "Geceleri sinir tanimaz.", target_h - 280, font_subtitle, (*off_white, alpha))
            
        elif time < 9.0:
            prog = (time - 6.0) / 3.0
            bg = get_zoomed_crop(bg_images[1], prog)
            
            overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,100))
            frame = Image.alpha_composite(bg, overlay)
            
            draw = ImageDraw.Draw(frame)
            alpha = int(255 * get_alpha(time, 6.0, 9.0))
            draw_text_elegant(draw, "2. E L I F", target_h - 450, font_title, (*gold, alpha))
            draw_text_elegant(draw, "Otoriter ve acimasiz.", target_h - 350, font_subtitle, (*white, alpha))
            draw_text_elegant(draw, "Itaat etmeye hazir misin?", target_h - 280, font_subtitle, (*off_white, alpha))
            
        elif time < 12.0:
            prog = (time - 9.0) / 3.0
            bg = get_zoomed_crop(bg_images[2], prog)
            
            overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,100))
            frame = Image.alpha_composite(bg, overlay)
            
            draw = ImageDraw.Draw(frame)
            alpha = int(255 * get_alpha(time, 9.0, 12.0))
            draw_text_elegant(draw, "3. Y U K I", target_h - 450, font_title, (*gold, alpha))
            draw_text_elegant(draw, "Utangac gorunur ama...", target_h - 350, font_subtitle, (*white, alpha))
            draw_text_elegant(draw, "Sadece elit uyelere ozel.", target_h - 280, font_subtitle, (*off_white, alpha))
            
        elif time < 15.0:
            prog = (time - 12.0) / 3.0
            bg = get_zoomed_crop(bg_images[3], prog)
            
            overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,100))
            frame = Image.alpha_composite(bg, overlay)
            
            draw = ImageDraw.Draw(frame)
            alpha = int(255 * get_alpha(time, 12.0, 15.0))
            draw_text_elegant(draw, "4. D E F N E", target_h - 450, font_title, (*gold, alpha))
            draw_text_elegant(draw, "Luks, pahali ve kiskirtici.", target_h - 350, font_subtitle, (*white, alpha))
            draw_text_elegant(draw, "Ona yetebilecek misin?", target_h - 280, font_subtitle, (*off_white, alpha))
            
        else:
            # Outro
            bg = get_zoomed_crop(bg_images[3], 1.0)
            overlay = Image.new('RGBA', (target_w, target_h), (0,0,0,220)) # Very dark
            frame = Image.alpha_composite(bg, overlay)
            
            draw = ImageDraw.Draw(frame)
            alpha = int(255 * get_alpha(time, 15.0, 16.0))
            draw_text_elegant(draw, "SECIMINI YAP.", target_h/2 - 100, font_title, (*gold, alpha))
            draw_text_elegant(draw, "VIP Erisim Linki Biyografide", target_h/2 + 20, font_subtitle, (*white, alpha))
            
        # Add cinematic black bars (letterboxing)
        draw = ImageDraw.Draw(frame)
        bar_height = 180
        draw.rectangle([0, 0, target_w, bar_height], fill=(0,0,0,255))
        draw.rectangle([0, target_h - bar_height, target_w, target_h], fill=(0,0,0,255))
            
        # Convert to BGR for OpenCV
        rgb_frame = frame.convert("RGB")
        bgr_frame = cv2.cvtColor(np.array(rgb_frame), cv2.COLOR_RGB2BGR)
        
        out.write(bgr_frame)
        
    out.release()
    print(f"\nProfesyonel VIP video bashariyla kaydedildi: {output_path}")

if __name__ == "__main__":
    base_dir = r"C:\Users\tolga\.gemini\antigravity\brain\fea51c54-51e5-4e4b-8654-bdd98786f35b"
    images = [
        os.path.join(base_dir, "ailoverbot_profile_picture_v5_1772977295319.png"),
        os.path.join(base_dir, "elif_promo_post_1773007540180.png"),
        os.path.join(base_dir, "yuki_promo_post_1773007556507.png"),
        os.path.join(base_dir, "defne_promo_post_1773007575314.png")
    ]
    out_path = "AILoverBot_Agency_TikTok_PRO.mp4"
    create_pro_agency_video(images, out_path)
