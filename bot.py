import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters
from config import TELEGRAM_BOT_TOKEN, PROACTIVE_CHECK_INTERVAL_HOURS
from database.models import init_db
from handlers.chat import (
    start_command, help_command, profile_command, 
    handle_message, handle_voice,
    characters_command, switch_character_command
)
from handlers.payment import buy_command, button_callback, precheckout_callback, successful_payment_callback
from services.proactive_service import check_and_send_proactive_messages

# Log ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Bot başlatıldıktan sonra proaktif mesaj scheduler'ı kur."""
    logger.info("Proaktif mesaj scheduler başlatılıyor...")
    
    async def scheduled_proactive():
        while True:
            await asyncio.sleep(PROACTIVE_CHECK_INTERVAL_HOURS * 3600)
            try:
                await check_and_send_proactive_messages(application)
            except Exception as e:
                logger.error(f"Proaktif mesaj scheduler hatası: {e}")
    
    asyncio.create_task(scheduled_proactive())
    logger.info(f"Proaktif mesaj scheduler kuruldu. Her {PROACTIVE_CHECK_INTERVAL_HOURS} saatte bir kontrol edilecek.")

def main():
    print("=" * 50)
    print("   AILoverBot - Sanal AI Partner v2.0")
    print("=" * 50)
    
    print("\n[*] Veritabani baslatiliyor...")
    init_db()
    
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("[X] Lutfen .env dosyasina TELEGRAM_BOT_TOKEN degerini girin.")
        return

    print("[*] Bot uygulamasi kuruluyor...")
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()
    
    # ===== KOMUTLAR =====
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('profile', profile_command))
    application.add_handler(CommandHandler('buy', buy_command))
    application.add_handler(CommandHandler('karakterler', characters_command))
    application.add_handler(CommandHandler('karakter', switch_character_command))
    
    # ===== ODEME ISLEYICILERI =====
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # ===== MESAJ ISLEYICILERI =====
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    print("\n[OK] Bot basariyla kuruldu!")
    print("[*] Karakterler: Mia, Elif, Yuki, Defne")
    print("[*] Odeme: Telegram Stars + Kripto + Test Modu")
    print("[*] Sesli mesaj: Whisper STT aktif")
    print("[*] Proaktif mesajlasma: Aktif")
    print("\n[>>>] Bot dinlemeye basliyor...\n")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
