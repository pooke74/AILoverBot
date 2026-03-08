import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Whisper STT için
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Gemini LLM (birincil)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ailover.db")
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")  # Telegram Stars
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "")  # Senin telegram ID'n

# LLM Ayarları
LLM_MODEL = "meta-llama/llama-3.2-3b-instruct:free"
LLM_FALLBACK_MODELS = [
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "google/gemma-3-4b-it:free",
]
DEFAULT_CREDITS = 50

# Proaktif Mesajlaşma (saat cinsinden)
PROACTIVE_CHECK_INTERVAL_HOURS = 6   # Her 6 saatte bir kontrol et
PROACTIVE_SILENCE_THRESHOLD_HOURS = 24  # 24 saat sessiz kalırsa mesaj at
