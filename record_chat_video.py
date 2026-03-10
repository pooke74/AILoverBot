import http.server
import threading
import time
import cv2
import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os

def start_server(port=8765, directory="."):
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=directory, **kwargs)
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd

def record_chat_video(output_path, duration=42, fps=15):
    print("Selenium ile gelistirmis Telegram sohbet kaydediliyor...")
    
    bot_dir = r"C:\Users\tolga\.gemini\antigravity\scratch\AILoverBot"
    httpd = start_server(port=8765, directory=bot_dir)
    time.sleep(1)
    
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
    except Exception as e:
        print(f"Chrome bulunamadi, Edge deneniyor: {e}")
        from selenium.webdriver.edge.options import Options as EdgeOptions
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--window-size=420,900")
        edge_options.add_argument("--force-device-scale-factor=2")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("--hide-scrollbars")
        driver = webdriver.Edge(options=edge_options)
    
    driver.get("http://127.0.0.1:8765/telegram_chat_sim.html")
    time.sleep(2)
    
    total_frames = int(duration * fps)
    interval = 1.0 / fps
    
    # Get screenshot dimensions for the video writer
    screenshot = driver.get_screenshot_as_png()
    img = Image.open(__import__('io').BytesIO(screenshot))
    w, h = img.size
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    
    print(f"Kayit basliyor: {w}x{h}, {fps} FPS, {duration} saniye, toplam {total_frames} kare...")
    
    start_time = time.time()
    for i in range(total_frames):
        target_time = start_time + (i * interval)
        
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(__import__('io').BytesIO(screenshot))
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        out.write(frame)
        
        # Wait until the next frame timing
        now = time.time()
        sleep_time = target_time - now
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        if i % 30 == 0:
            elapsed = time.time() - start_time
            print(f"  Kare {i}/{total_frames} ({elapsed:.1f}s gecti)")
    
    out.release()
    driver.quit()
    httpd.shutdown()
    print(f"\nVideo basariyla kaydedildi: {output_path}")

if __name__ == "__main__":
    out = r"C:\Users\tolga\.gemini\antigravity\brain\fea51c54-51e5-4e4b-8654-bdd98786f35b\AILoverBot_Chat_Simulation.mp4"
    record_chat_video(out, duration=42, fps=15)
