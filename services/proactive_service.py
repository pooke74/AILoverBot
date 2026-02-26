import random
import logging
from datetime import datetime, timedelta
from database.models import SessionLocal, User, Message
from services.llm_service import generate_response
from services.audio_service import generate_audio
from prompts.character import get_character
from config import PROACTIVE_SILENCE_THRESHOLD_HOURS

logger = logging.getLogger(__name__)

# Proaktif mesaj metinleri her karakterde tanımlı (prompts/character.py)

async def check_and_send_proactive_messages(application):
    """
    Belirli süre boyunca sessiz kalan kullanıcılara otomatik "Seni özledim" mesajı atar.
    APScheduler tarafından periyodik olarak çağrılır.
    """
    logger.info("Proaktif mesaj kontrolü başlatılıyor...")
    threshold = datetime.utcnow() - timedelta(hours=PROACTIVE_SILENCE_THRESHOLD_HOURS)
    
    with SessionLocal() as session:
        # Son X saat içinde hiç aktif olmayan kullanıcıları bul
        inactive_users = session.query(User).filter(
            User.last_active < threshold,
            User.credits > 0  # Sadece kredisi olanlara mesaj at (kredisi bitmişlere atma)
        ).all()
        
        for user in inactive_users:
            try:
                char = get_character(user.selected_character)
                
                # Rastgele bir proaktif mesaj seç
                proactive_msg = random.choice(char['proactive_messages'])
                
                # Telegram'a mesaj gönder
                await application.bot.send_message(
                    chat_id=user.telegram_id,
                    text=proactive_msg
                )
                
                # Mesajı veritabanına kaydet
                bot_msg = Message(
                    user_id=user.id,
                    role='assistant',
                    content=proactive_msg,
                    character_id=user.selected_character
                )
                session.add(bot_msg)
                
                # Arada bir sesli not da gönder (%20 ihtimalle)
                if random.random() < 0.20:
                    audio_path = await generate_audio(proactive_msg)
                    if audio_path:
                        import os
                        await application.bot.send_voice(
                            chat_id=user.telegram_id,
                            voice=open(audio_path, 'rb')
                        )
                        os.remove(audio_path)
                
                # last_active'i güncelle ki aynı kullanıcıya tekrar atmasın
                user.last_active = datetime.utcnow()
                
                logger.info(f"Proaktif mesaj gönderildi: user_id={user.telegram_id}, karakter={char['name']}")
                
            except Exception as e:
                logger.error(f"Proaktif mesaj hatası (user_id={user.telegram_id}): {e}")
                continue
        
        session.commit()
    
    logger.info(f"Proaktif mesaj kontrolü tamamlandı. {len(inactive_users)} kullanıcıya mesaj gönderildi.")
