import os
import random
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database.models import SessionLocal, User, Message
from services.llm_service import generate_response
from services.image_service import generate_image
from services.audio_service import generate_audio
from services.stt_service import transcribe_voice
from prompts.character import get_character, list_characters, CHARACTERS

def get_or_create_user(session: Session, tg_user):
    user = session.query(User).filter(User.telegram_id == tg_user.id).first()
    if not user:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            credits=50,
            selected_character='mia',
            last_active=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

# ===================== KOMUTLAR =====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char = get_character(user.selected_character)
        await update.message.reply_text(
            f"Selam {user.first_name}! Ben {char['name']}. {char['emoji']}\n"
            f"Seninle tanıştığıma çok sevindim!\n\n"
            f"💎 Kredin: {user.credits}\n"
            f"🎭 Aktif Karakter: {char['name']}\n\n"
            f"Bana dilediğin her şeyi yazabilirsin!\n"
            f"Sesli mesaj da gönderebilirsin, seni anlayabilirim 🎤\n\n"
            f"📋 Komutlar:\n"
            f"/karakterler - Karakter listesi\n"
            f"/karakter [isim] - Karakter değiştir\n"
            f"/profile - Profilin\n"
            f"/buy - Kredi satın al"
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💖 Bana metin veya sesli mesaj gönderebilirsin!\n\n"
        "📋 **Komutlar:**\n"
        "/karakterler - Tüm karakterleri gör\n"
        "/karakter [isim] - Karakter değiştir\n"
        "/profile - Kredin ve profilin\n"
        "/buy - Kredi satın al\n\n"
        "💰 **Kredi Detayları:**\n"
        "  ✏️ Metin mesajı: 1 kredi\n"
        "  🎤 Sesli yanıt: 5 kredi\n"
        "  📸 Fotoğraf: 10 kredi",
        parse_mode='Markdown'
    )
    
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char = get_character(user.selected_character)
        vip_text = "👑 VIP Üye" if user.is_vip else "💎 Standart"
        await update.message.reply_text(
            f"👤 **Profilin**\n\n"
            f"Kalan Kredin: {user.credits} 💎\n"
            f"Üyelik: {vip_text}\n"
            f"Aktif Karakter: {char['emoji']} {char['name']}\n"
            f"Kayıt Tarihi: {user.created_at.strftime('%d.%m.%Y')}\n\n"
            f"Kredi almak için /buy yazabilirsin.",
            parse_mode='Markdown'
        )

async def characters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm karakterleri listeler."""
    await update.message.reply_text(list_characters(), parse_mode='Markdown')

async def switch_character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcının aktif karakterini değiştirir."""
    if not context.args:
        await update.message.reply_text(
            "Karakter seçmek için karakter ismini yaz!\n"
            "Örnek: `/karakter elif`\n\n"
            "Mevcut karakterler: " + ", ".join(CHARACTERS.keys()),
            parse_mode='Markdown'
        )
        return
    
    char_id = context.args[0].lower()
    
    if char_id not in CHARACTERS:
        await update.message.reply_text(
            f"❌ '{char_id}' diye bir karakter yok.\n"
            f"Mevcut karakterler: {', '.join(CHARACTERS.keys())}"
        )
        return
    
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        user.selected_character = char_id
        session.commit()
        
        char = get_character(char_id)
        await update.message.reply_text(
            f"{char['emoji']} Harika! Artık **{char['name']}** ile sohbet ediyorsun!\n\n"
            f"_{char['description']}_\n\n"
            f"Hadi, bana bir şeyler yaz! 💬",
            parse_mode='Markdown'
        )

# ===================== MESAJ İŞLEYİCİLER =====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metin mesajı işleyicisi."""
    user_text = update.message.text
    if not user_text:
        return
    await _process_user_input(update, context, user_text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sesli mesaj işleyicisi (Feature 5: Voice Input).
    Kullanıcının sesli mesajını Whisper ile metne çevirir, sonra normal metin gibi işler.
    """
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Sesli mesajı indir
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    
    os.makedirs("temp_audio", exist_ok=True)
    local_path = f"temp_audio/voice_{update.effective_user.id}_{voice.file_unique_id}.ogg"
    await file.download_to_drive(local_path)
    
    # Whisper ile metne çevir
    transcription = await transcribe_voice(local_path)
    
    if not transcription:
        await update.message.reply_text("Sesini tam duyamadım, tekrar söyler misin? 🎤")
        return
    
    # Kullanıcıya ne anladığını göster (şeffaflık)
    await update.message.reply_text(f"🎤 _\"{transcription}\"_", parse_mode='Markdown')
    
    # Normal mesaj gibi işle
    await _process_user_input(update, context, transcription, force_voice_response=True)

async def _process_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str, force_voice_response: bool = False):
    """
    Hem metin hem sesli mesaj için ortak işleme mantığı.
    force_voice_response=True ise cevap sesli olarak gönderilir.
    """
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char_id = user.selected_character
        
        if user.credits <= 0 and not user.is_vip:
            char = get_character(char_id)
            await update.message.reply_text(
                f"Tatlım, maalesef kredin bitmiş 😢\n"
                f"Benimle konuşmaya devam etmek için /buy yazarak kredi alabilirsin!"
            )
            return
        
        # Kullanıcı mesajını kaydet
        user_msg = Message(user_id=user.id, role='user', content=user_text, character_id=char_id)
        session.add(user_msg)
        
        # Kredi düş (VIP değilse)
        if not user.is_vip:
            user.credits -= 1
        
        # last_active güncelle
        user.last_active = datetime.utcnow()
        
        # Geçmiş 10 mesajı al (aynı karakter bazında)
        past_messages = session.query(Message).filter(
            Message.user_id == user.id,
            Message.character_id == char_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        past_messages.reverse()
        
        chat_history = [{"role": msg.role, "content": msg.content} for msg in past_messages]
        session.commit()
        
    # LLM cevabı al (karakter bazlı)
    bot_response = await generate_response(chat_history, character_id=char_id)
    
    # [GÖRSEL GÖNDER] kontrolü
    img_requested = False
    if "[GÖRSEL GÖNDER]" in bot_response:
        img_requested = True
        bot_response = bot_response.replace("[GÖRSEL GÖNDER]", "").strip()

    with SessionLocal() as db_session:
        user = get_or_create_user(db_session, update.effective_user)
        # Asistan mesajını kaydet
        bot_msg = Message(user_id=user.id, role='assistant', content=bot_response, character_id=char_id)
        db_session.add(bot_msg)
        
        if bot_response:
            # Sesli yanıt mantığı
            should_send_voice = force_voice_response
            if not should_send_voice:
                if "sesi" in user_text.lower() or "konuş" in user_text.lower() or random.random() < 0.05:
                    should_send_voice = True
                    
            if should_send_voice and (user.credits >= 4 or user.is_vip):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
                audio_path = await generate_audio(bot_response)
                
                if audio_path:
                    if not user.is_vip:
                        user.credits -= 4
                    await update.message.reply_voice(voice=open(audio_path, 'rb'))
                    os.remove(audio_path)
                else:
                    await update.message.reply_text(bot_response)
            else:
                await update.message.reply_text(bot_response)

        # Görsel gönderme
        if img_requested:
            if user.credits >= 9 or user.is_vip:
                await update.message.reply_text("(Hazırlanıyorum... Fotoğraf birazdan gelecek 📸)")
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
                
                img_url = await generate_image(bot_response, character_id=char_id)
                
                if img_url:
                    if not user.is_vip:
                        user.credits -= 9
                    await update.message.reply_photo(photo=img_url)
                else:
                    await update.message.reply_text("Kameram bozuldu tatlım, şu an çekemiyorum 😢")
            else:
                await update.message.reply_text("Sana özel bir fotoğraf atacaktım ama kredin yetmiyor tatlım. 😢 (/buy)")
        
        db_session.commit()
