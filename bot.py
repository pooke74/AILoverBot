import logging
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, PreCheckoutQueryHandler, filters
from config import TELEGRAM_BOT_TOKEN, PROACTIVE_CHECK_INTERVAL_HOURS
from database.models import init_db
from handlers.chat import (
    start_command, help_command, profile_command, 
    handle_message, handle_voice,
    characters_command, switch_character_command,
    menu_command, menu_callback, referral_command,
    gift_command, gift_callback, sexting_command,
    create_custom_persona_command,
    admin_foto_command, admin_trip_command
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
    print("   AILoverBot - Sanal AI Partner v2.1")
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
    application.add_handler(CommandHandler('menu', menu_command))
    application.add_handler(CommandHandler('profile', profile_command))
    application.add_handler(CommandHandler('buy', buy_command))
    application.add_handler(CommandHandler('karakterler', characters_command))
    application.add_handler(CommandHandler('karakter', switch_character_command))
    application.add_handler(CommandHandler('davet', referral_command))
    application.add_handler(CommandHandler('hediye', gift_command))
    application.add_handler(CommandHandler('sexting', sexting_command))
    application.add_handler(CommandHandler('yarat', create_custom_persona_command))
    
    # Marketing / TikTok
    application.add_handler(CommandHandler('tiktok_foto', admin_foto_command))
    application.add_handler(CommandHandler('tiktok_trip', admin_trip_command))
    
    # ===== ODEME ISLEYICILERI =====
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    
    # ===== MENU + ODEME BUTON CALLBACK =====
    application.add_handler(CallbackQueryHandler(menu_callback, pattern="^(menu_|select_char_)"))
    application.add_handler(CallbackQueryHandler(gift_callback, pattern="^gift_"))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # ===== MESAJ ISLEYICILERI =====
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # ===== GLOBAL HATA ISLEYICI =====
    async def error_handler(update, context):
        logger.error(f"Hata: {context.error}", exc_info=context.error)
        # Kullaniciya nazik hata mesaji
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "Bir sorun olustu, tekrar dener misin? Hemen duzeltiyorum!"
                )
        except:
            pass
    
    application.add_error_handler(error_handler)
    
    print("\n[OK] Bot basariyla kuruldu!")
    print("[*] v2.1 - OpenAI + Gemini + Referans Foto")
    print("[*] Karakterler: Mia, Elif, Yuki, Defne")
    print("[*] Odeme: Telegram Stars + Kripto")
    print("[*] Sesli: ElevenLabs TTS + Whisper STT")
    print("[*] Proaktif mesajlasma: Aktif")
    print("\n[>>>] Bot dinlemeye basliyor...\n")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
