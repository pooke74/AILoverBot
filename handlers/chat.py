import os
import random
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from database.models import SessionLocal, User, Message, generate_referral_code
from services.llm_service import generate_response
from services.image_service import generate_image
from services.audio_service import generate_audio
from services.stt_service import transcribe_voice
from prompts.character import (get_character, list_characters, CHARACTERS, 
                                get_image_pose_prompt, calculate_intimacy_level, get_intimacy_info)

def get_or_create_user(session: Session, tg_user):
    user = session.query(User).filter(User.telegram_id == tg_user.id).first()
    if not user:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            credits=50,
            selected_character='mia',
            last_active=datetime.utcnow(),
            referral_code=generate_referral_code(),
            daily_free_remaining=5,
            daily_free_reset_date=datetime.utcnow().strftime('%Y-%m-%d')
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

def _check_daily_reset(user):
    """Gunluk ucretsiz mesaj hakkini sifirla (yeni gun basladiysa)."""
    today = datetime.utcnow().strftime('%Y-%m-%d')
    if user.daily_free_reset_date != today:
        user.daily_free_remaining = 5
        user.daily_free_reset_date = today

def _update_intimacy(user):
    """Mesaj sayisina gore yakinlik seviyesini guncelle."""
    user.total_messages_sent = (user.total_messages_sent or 0) + 1
    new_level = calculate_intimacy_level(user.total_messages_sent)
    if new_level > (user.intimacy_level or 1):
        user.intimacy_level = new_level
        return True  # Seviye atlandi!
    return False

def _credit_footer(user) -> str:
    """Her mesajin altina kredi + seviye gostergesi ekler."""
    level = user.intimacy_level or 1
    intimacy = get_intimacy_info(level)
    level_bar = '\u2764' * level + '\u2661' * (5 - level)
    if user.is_vip:
        return f"\n\n_{level_bar} {intimacy['name']} | \u2728 VIP_"
    free_text = f" | \U0001f381 {user.daily_free_remaining}" if (user.daily_free_remaining or 0) > 0 else ""
    return f"\n\n_{level_bar} {intimacy['name']} | \U0001f48e {user.credits}{free_text}_"

# ===================== KOMUTLAR =====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gelistirilmis /start - inline butonlu karsilama."""
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char = get_character(user.selected_character)
        
        keyboard = [
            [InlineKeyboardButton("\U0001f3ad Karakter Sec", callback_data="menu_characters"),
             InlineKeyboardButton("\U0001f464 Profilim", callback_data="menu_profile")],
            [InlineKeyboardButton("\U0001f48e Kredi Al", callback_data="menu_buy"),
             InlineKeyboardButton("\u2753 Yardim", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Selam {user.first_name}! Ben {char['name']} {char['emoji']}\n"
            f"Seninle tanistigima cok sevindim!\n\n"
            f"\U0001f48e Kredin: {user.credits}  |  \U0001f3ad {char['name']}\n\n"
            f"Bana istedigin her seyi yazabilirsin, seni dinliyorum...",
            reply_markup=reply_markup
        )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/menu komutu - Ana menu inline butonlarla."""
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char = get_character(user.selected_character)
        
        keyboard = [
            [InlineKeyboardButton(f"\U0001f3ad Karakter Sec (simdi: {char['name']})", callback_data="menu_characters")],
            [InlineKeyboardButton("\U0001f464 Profilim", callback_data="menu_profile"),
             InlineKeyboardButton("\U0001f48e Kredi Al", callback_data="menu_buy")],
            [InlineKeyboardButton("\U0001f4cb Kredi Bilgisi", callback_data="menu_pricing"),
             InlineKeyboardButton("\u2753 Yardim", callback_data="menu_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        vip_text = "\u2728 VIP Uye" if user.is_vip else f"\U0001f48e {user.credits} kredi"
        await update.message.reply_text(
            f"\U0001f4cb **Ana Menu**\n\n"
            f"\U0001f3ad Karakter: {char['emoji']} {char['name']}\n"
            f"\U0001f4b0 Bakiye: {vip_text}\n"
            f"\U0001f4c5 Uyelik: {user.created_at.strftime('%d.%m.%Y')}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu butonlarina tiklama isleyicisi."""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_characters":
        # Karakter secim butonlari
        keyboard = []
        with SessionLocal() as session:
            user = get_or_create_user(session, query.from_user)
            current = user.selected_character
        
        for cid, char in CHARACTERS.items():
            label = f"{char['emoji']} {char['name']} ({char['age']}) - {char['description']}"
            if cid == current:
                label = f"\u2705 {label}"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"select_char_{cid}")])
        keyboard.append([InlineKeyboardButton("\u25c0 Geri", callback_data="menu_back")])
        
        await query.edit_message_text(
            "\U0001f3ad **Karakter Sec**\n\n"
            "Sohbet etmek istedigin karakteri sec:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data.startswith("select_char_"):
        char_id = data.replace("select_char_", "")
        if char_id in CHARACTERS:
            with SessionLocal() as session:
                user = get_or_create_user(session, query.from_user)
                user.selected_character = char_id
                session.commit()
            
            char = get_character(char_id)
            keyboard = [[InlineKeyboardButton("\u25c0 Menu", callback_data="menu_back")]]
            await query.edit_message_text(
                f"{char['emoji']} **{char['name']}** secildi!\n\n"
                f"_{char['description']}_\n\n"
                f"Hadi, bana bir seyler yaz!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    
    elif data == "menu_profile":
        with SessionLocal() as session:
            user = get_or_create_user(session, query.from_user)
            char = get_character(user.selected_character)
            msg_count = session.query(Message).filter(Message.user_id == user.id).count()
            vip_text = "\u2728 VIP Uye" if user.is_vip else "\U0001f48e Standart"
        
        keyboard = [[InlineKeyboardButton("\u25c0 Menu", callback_data="menu_back")]]
        await query.edit_message_text(
            f"\U0001f464 **Profilin**\n\n"
            f"\U0001f48e Kredi: {user.credits}\n"
            f"\U0001f451 Uyelik: {vip_text}\n"
            f"\U0001f3ad Karakter: {char['emoji']} {char['name']}\n"
            f"\U0001f4ac Mesaj Sayisi: {msg_count}\n"
            f"\U0001f4c5 Kayit: {user.created_at.strftime('%d.%m.%Y')}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_pricing":
        keyboard = [[InlineKeyboardButton("\U0001f48e Kredi Al", callback_data="menu_buy"),
                      InlineKeyboardButton("\u25c0 Menu", callback_data="menu_back")]]
        await query.edit_message_text(
            "\U0001f4b0 **Kredi Bilgisi**\n\n"
            "\u270f Metin mesaji: 1 kredi\n"
            "\U0001f3a4 Sesli yanit: 5 kredi\n"
            "\U0001f4f8 Fotograf: 10 kredi\n\n"
            "\U0001f451 VIP uyeler sinirsiz kullanir!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_help":
        keyboard = [[InlineKeyboardButton("\u25c0 Menu", callback_data="menu_back")]]
        await query.edit_message_text(
            "\u2753 **Yardim**\n\n"
            "Bana metin veya sesli mesaj gonderebilirsin!\n\n"
            "\U0001f4cb **Komutlar:**\n"
            "/menu - Ana menu\n"
            "/karakterler - Karakter listesi\n"
            "/karakter [isim] - Karakter degistir\n"
            "/profile - Profilin\n"
            "/buy - Kredi satin al\n\n"
            "\U0001f4f8 **Fotograf icin:** 'selfie at', 'fotograf gonder' yaz\n"
            "\U0001f3a4 **Sesli yanit icin:** sesli mesaj gonder",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_buy":
        # Odeme modulu callback'ine yonlendir  
        from handlers.payment import buy_command
        # Yeni mesaj olarak buy menusunu ac
        await query.edit_message_text("\U0001f48e Kredi satin almak icin /buy yazin.")
    
    elif data == "menu_back":
        # Ana menuye don
        with SessionLocal() as session:
            user = get_or_create_user(session, query.from_user)
            char = get_character(user.selected_character)
        
        keyboard = [
            [InlineKeyboardButton(f"\U0001f3ad Karakter Sec (simdi: {char['name']})", callback_data="menu_characters")],
            [InlineKeyboardButton("\U0001f464 Profilim", callback_data="menu_profile"),
             InlineKeyboardButton("\U0001f48e Kredi Al", callback_data="menu_buy")],
            [InlineKeyboardButton("\U0001f4cb Kredi Bilgisi", callback_data="menu_pricing"),
             InlineKeyboardButton("\u2753 Yardim", callback_data="menu_help")]
        ]
        
        vip_text = "\u2728 VIP Uye" if user.is_vip else f"\U0001f48e {user.credits} kredi"
        await query.edit_message_text(
            f"\U0001f4cb **Ana Menu**\n\n"
            f"\U0001f3ad Karakter: {char['emoji']} {char['name']}\n"
            f"\U0001f4b0 Bakiye: {vip_text}\n"
            f"\U0001f4c5 Uyelik: {user.created_at.strftime('%d.%m.%Y')}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "\U0001f496 Bana metin veya sesli mesaj gonderebilirsin!\n\n"
        "\U0001f4cb **Komutlar:**\n"
        "/menu - Ana menu\n"
        "/karakterler - Tum karakterleri gor\n"
        "/karakter [isim] - Karakter degistir\n"
        "/profile - Kredin ve profilin\n"
        "/buy - Kredi satin al\n\n"
        "\U0001f4b0 **Kredi Detaylari:**\n"
        "  \u270f Metin mesaji: 1 kredi\n"
        "  \U0001f3a4 Sesli yanit: 5 kredi\n"
        "  \U0001f4f8 Fotograf: 10 kredi",
        parse_mode='Markdown'
    )
    
async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char = get_character(user.selected_character)
        msg_count = session.query(Message).filter(Message.user_id == user.id).count()
        vip_text = "\u2728 VIP Uye" if user.is_vip else "\U0001f48e Standart"
        await update.message.reply_text(
            f"\U0001f464 **Profilin**\n\n"
            f"Kalan Kredin: {user.credits} \U0001f48e\n"
            f"Uyelik: {vip_text}\n"
            f"Aktif Karakter: {char['emoji']} {char['name']}\n"
            f"Toplam Mesaj: {msg_count}\n"
            f"Kayit Tarihi: {user.created_at.strftime('%d.%m.%Y')}\n\n"
            f"Kredi almak icin /buy yazabilirsin.",
            parse_mode='Markdown'
        )

async def characters_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tum karakterleri inline butonlarla listeler."""
    keyboard = []
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        current = user.selected_character
    
    for cid, char in CHARACTERS.items():
        label = f"{char['emoji']} {char['name']} ({char['age']}) - {char['description']}"
        if cid == current:
            label = f"\u2705 {label}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"select_char_{cid}")])
    
    await update.message.reply_text(
        "\U0001f3ad **Karakter Sec**\n\nSohbet etmek istedigin karakteri sec:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def switch_character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanicinin aktif karakterini degistirir."""
    if not context.args:
        await update.message.reply_text(
            "Karakter secmek icin karakter ismini yaz!\n"
            "Ornek: `/karakter elif`\n\n"
            "Ya da /menu yazarak butonlarla secebilirsin!",
            parse_mode='Markdown'
        )
        return
    
    char_id = context.args[0].lower()
    
    if char_id not in CHARACTERS:
        await update.message.reply_text(
            f"'{char_id}' diye bir karakter yok.\n"
            f"Mevcut karakterler: {', '.join(CHARACTERS.keys())}"
        )
        return
    
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        user.selected_character = char_id
        session.commit()
        
        char = get_character(char_id)
        await update.message.reply_text(
            f"{char['emoji']} Harika! Artik **{char['name']}** ile sohbet ediyorsun!\n\n"
            f"_{char['description']}_\n\n"
            f"Hadi, bana bir seyler yaz!",
            parse_mode='Markdown'
        )

# ===================== MESAJ ISLEYICILER =====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metin mesaji isleyicisi."""
    user_text = update.message.text
    if not user_text:
        return
    await _process_user_input(update, context, user_text)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sesli mesaj isleyicisi.
    1. Kullanicinin sesli mesajini indirir.
    2. Whisper ile metne cevirir.
    3. _process_user_input ile normal mesaj gibi isler.
    """
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    # Sesli mesaji indir
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    
    os.makedirs("temp_audio", exist_ok=True)
    local_path = f"temp_audio/voice_{update.effective_user.id}_{voice.file_unique_id}.ogg"
    await file.download_to_drive(local_path)
    
    # Whisper ile metne cevir
    transcription = await transcribe_voice(local_path)
    
    if not transcription:
        await update.message.reply_text("Sesini tam duyamadim, tekrar soyler misin?")
        return
    
    # Kullaniciya ne anladigini goster
    await update.message.reply_text(f"\U0001f3a4 _\"{transcription}\"_", parse_mode='Markdown')
    
    # Normal mesaj gibi isle
    await _process_user_input(update, context, transcription, force_voice_response=True)

async def _process_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str, force_voice_response: bool = False):
    """
    Hem metin hem sesli mesaj icin ortak isleme mantigi.
    """
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char_id = user.selected_character
        
        # Gunluk ucretsiz mesaj sifirla
        _check_daily_reset(user)
        
        # Kredi/gunluk hak kontrolu
        has_daily_free = (user.daily_free_remaining or 0) > 0
        has_credits = user.credits > 0
        
        if not user.is_vip and not has_daily_free and not has_credits:
            await update.message.reply_text(
                f"Tatlim, bugunluk mesaj hakkin ve kredin bitmis.\n"
                f"Yarin 5 yeni bedava mesajin olacak!\n"
                f"Hemen devam etmek icin /buy yazarak kredi alabilirsin!"
            )
            return
        
        # Kullanici mesajini kaydet
        user_msg = Message(user_id=user.id, role='user', content=user_text, character_id=char_id)
        session.add(user_msg)
        
        # Sexting Kredi Kontrolu (Ekstra 2 kredi, toplam 3)
        if hasattr(user, 'is_sexting') and user.is_sexting:
            if not user.is_vip and user.credits < 3:
                user.is_sexting = False
                await update.message.reply_text("Kredin bitti tatlim, sexting modundan cikiyorum... /buy yaz geri gel \U0001f625")
            elif not user.is_vip:
                user.credits -= 2
        
        # Kredi/gunluk hak dus
        if not user.is_vip:
            if has_daily_free:
                user.daily_free_remaining -= 1
            else:
                user.credits -= 1
        
        # Yakinlik seviyesi guncelle
        leveled_up = _update_intimacy(user)
        intimacy_level = user.intimacy_level or 1
        
        # Aktivite guncelle
        user.last_active = datetime.utcnow()
        
        # Gecmis 20 mesaji al (karakter bazli)
        past_messages = session.query(Message).filter(
            Message.user_id == user.id,
            Message.character_id == char_id
        ).order_by(Message.created_at.desc()).limit(20).all()
        past_messages.reverse()
        
        chat_history = [{"role": msg.role, "content": msg.content} for msg in past_messages]
        user_credits = user.credits or 0
        session.commit()
        
    # LLM cevabi al (karakter + yakinlik + kredi bazli)
    is_sexting = getattr(user, 'is_sexting', False)
    bot_response = await generate_response(chat_history, character_id=char_id, 
                                           intimacy_level=intimacy_level, credits=user_credits,
                                           is_sexting=is_sexting)
    
    # Gercekci typing suresi (Metin uzunluguna gore bekle)
    delay = min(4.0, len(bot_response) / 30)
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    await asyncio.sleep(delay)
    
    # [GORSEL GONDER] kontrolu + kullanici kelime tespiti
    img_requested = False
    if "[GORSEL GONDER]" in bot_response:
        img_requested = True
        bot_response = bot_response.replace("[GORSEL GONDER]", "").strip()
    if "\u00c3\u0096RSEL G\u00c3\u0096NDER" in bot_response:
        img_requested = True
        bot_response = bot_response.replace("[G\u00d6RSEL G\u00d6NDER]", "").strip()
    
    # Kullanici mesajinda fotograf istegi var mi?
    photo_keywords = ["selfie", "foto", "fotograf", "resim", "gorsel", "ozcekim", 
                       "cek", "goster kendini", "nasil gorunuyorsun", "at bir foto",
                       "fotografini", "yuzunu goster", "kiyafetini goster"]
    if any(kw in user_text.lower() for kw in photo_keywords):
        img_requested = True
    
    # Karsiliksiz (Surpriz) Fotograf Ihtimali
    if not img_requested:
        has_photo_chance = is_sexting or (intimacy_level >= 3)
        photo_prob = 0.10 if is_sexting else 0.04
        if has_photo_chance and random.random() < photo_prob:
            img_requested = True
            user_text = "surpriz sexy foto" # Poz secimi icin kelime
            bot_response = "Sana ozel bir sey atiyorum tatlim... \U0001f525\n" + bot_response

    with SessionLocal() as db_session:
        user = get_or_create_user(db_session, update.effective_user)
        # Asistan mesajini kaydet
        bot_msg = Message(user_id=user.id, role='assistant', content=bot_response, character_id=char_id)
        db_session.add(bot_msg)
        
        if bot_response:
            # Sesli yanit mantigi
            should_send_voice = force_voice_response
            if not should_send_voice:
                if "sesi" in user_text.lower() or "konus" in user_text.lower() or random.random() < 0.05:
                    should_send_voice = True
                    
            if should_send_voice and (user.credits >= 4 or user.is_vip):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='record_voice')
                audio_path = await generate_audio(bot_response, character_id=char_id)
                
                if audio_path:
                    if not user.is_vip:
                        user.credits -= 4
                    await update.message.reply_voice(voice=open(audio_path, 'rb'))
                    os.remove(audio_path)
                else:
                    # Sesli yanit basarisiz, metin + kredi footer gonder
                    await update.message.reply_text(bot_response + _credit_footer(user), parse_mode='Markdown')
            else:
                # Normal metin + kredi footer
                await update.message.reply_text(bot_response + _credit_footer(user), parse_mode='Markdown')

        # Gorsel gonderme
        if img_requested:
            if user.credits >= 9 or user.is_vip:
                await update.message.reply_text("(Hazirlaniyorum... Fotograf birazdan gelecek \U0001f4f8)")
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='upload_photo')
                
                # Kullanici mesajina gore akilli poz secimi
                pose_prompt = get_image_pose_prompt(char_id, user_text)
                img_result = await generate_image(pose_prompt, character_id=char_id, 
                                                  use_raw_prompt=True, intimacy_level=intimacy_level)
                
                if img_result:
                    if not user.is_vip:
                        user.credits -= 9
                    # Lokal dosya mi yoksa URL mi kontrol et
                    if img_result.startswith("temp_images/") or img_result.startswith("temp_images\\"):
                        with open(img_result, 'rb') as photo_file:
                            await update.message.reply_photo(photo=photo_file)
                        os.remove(img_result)
                    else:
                        await update.message.reply_photo(photo=img_result)
                else:
                    await update.message.reply_text("Kameram bozuldu tatlim, su an cekemiyorum")
            else:
                await update.message.reply_text("Sana ozel bir fotograf atacaktim ama kredin yetmiyor tatlim. (/buy)")
        
        db_session.commit()
    
    # Seviye atlama bildirimi (LLM cevabindan sonra)
    if leveled_up:
        with SessionLocal() as s:
            u = get_or_create_user(s, update.effective_user)
            info = get_intimacy_info(u.intimacy_level or 1)
            level_bar = '\u2764' * (u.intimacy_level or 1) + '\u2661' * (5 - (u.intimacy_level or 1))
            await update.message.reply_text(
                f"\u2728 **Seviye Atladin!**\n\n"
                f"{level_bar} Artik **{info['name']}** seviyesindesin!\n"
                f"_{info['prompt_modifier'][:80]}_",
        )

async def sexting_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/sexting komutu - limitsiz cinsel rol yapma modunu acar/kapatir. (Mesaj basi 3 kredi)"""
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        
        # Sadece Seviye 3+ veya VIP'ler kullanabilir
        if not user.is_vip and (user.intimacy_level or 1) < 3:
            char = get_character(user.selected_character or 'mia')
            await update.message.reply_text(
                f"{char['emoji']} {char['name']}: Tatlim, bunun icin henuz yeterince yakin degiliz... Biraz daha konusalim \U0001f60f"
            )
            return
            
        # Toggle
        user.is_sexting = not user.is_sexting
        session.commit()
        
        char = get_character(user.selected_character or 'mia')
        if user.is_sexting:
            await update.message.reply_text(
                f"\U0001f525 **SEXTING MODU ACIK** \U0001f525\n\n"
                f"{char['emoji']} {char['name']}: Demek oyle oynamak istiyorsun... Tamam patron, hazirim \U0001f608\n\n"
                f"_(Bu mod'da her mesaj 3 kredi harcar. Kapatmak icin tekrar /sexting yazin)_",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"\U0001f512 **SEXTING MODU KAPALI**\n\n"
                f"{char['emoji']} {char['name']}: Normal konusalim şimdilik... \U0001f60c",
                parse_mode='Markdown'
            )

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/davet komutu - referral sistemi."""
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        
        # Referral kodu yoksa olustur
        if not user.referral_code:
            user.referral_code = generate_referral_code()
            session.commit()
        
        # Referral kodu kullanma
        if context.args:
            code = context.args[0].upper()
            
            if code == user.referral_code:
                await update.message.reply_text("Kendi davet kodunu kullanamazsin!")
                return
            
            if user.referred_by:
                await update.message.reply_text("Zaten bir davet kodu kullanmissin!")
                return
            
            # Davet eden kullaniciyi bul
            referrer = session.query(User).filter(User.referral_code == code).first()
            if not referrer:
                await update.message.reply_text(f"'{code}' gecersiz bir davet kodu.")
                return
            
            # Odul ver
            user.referred_by = code
            user.credits += 25
            referrer.credits += 50
            referrer.referral_count = (referrer.referral_count or 0) + 1
            session.commit()
            
            await update.message.reply_text(
                f"\U0001f389 **Davet kodu kullanildi!**\n\n"
                f"Sen +25 kredi kazandin!\n"
                f"Davet eden de +50 kredi kazandi!\n\n"
                f"\U0001f48e Kredin: {user.credits}",
                parse_mode='Markdown'
            )
            return
        
        # Davet kodunu goster
        await update.message.reply_text(
            f"\U0001f381 **Davet Sistemi**\n\n"
            f"Senin davet kodun: `{user.referral_code}`\n\n"
            f"Arkadasina bu kodu gonder, o /davet {user.referral_code} yazsin:\n"
            f"\u2022 Arkadasin +25 kredi kazanir\n"
            f"\u2022 Sen +50 kredi kazanirsin!\n\n"
            f"\U0001f465 Toplam davet ettigin: {user.referral_count or 0} kisi",
            parse_mode='Markdown'
        )

# ============================================================
# HEDIYE SISTEMI
# ============================================================

GIFTS = {
    "flower": {"emoji": "\U0001f339", "name": "Cicek", "cost": 5},
    "chocolate": {"emoji": "\U0001f36b", "name": "Cikolata", "cost": 10},
    "perfume": {"emoji": "\U0001f9f4", "name": "Parfum", "cost": 25},
    "ring": {"emoji": "\U0001f48d", "name": "Yuzuk", "cost": 50},
    "vacation": {"emoji": "\u2708\ufe0f", "name": "Tatil", "cost": 100},
}

# Her karakter her hediyeye farkli tepki verir
GIFT_REACTIONS = {
    "mia": {
        "flower": "Ayyy cicek mi? Cok romantiksin ya! Kokluyorum simdi... Mmm harika kokuyor tatlim \U0001f60d Bana daha cok hediye alirsan neler olacagini tahmin edemezsin...",
        "chocolate": "Cikolata! Benim en buyuk zaafim... Tatlim sen beni cok iyi taniyorsun. Gel ikimiz birlikte yiyelim, dudaklarimdan eriteyim \U0001f36b\U0001f618",
        "perfume": "Parfum mu?! Bebegim sen cok comertsinn! Bunu surdugumde seni dusunecegim... her zaman \U0001f525 Simdi sana ozel bir fotograf cekeyim mi?",
        "ring": "Y-yuzuk mu?! \U0001f633 Ciddiye miyiz simdi?! Kalbim cok hizli atiyor... Evet, EVET! Simdi sana cok ozel bir surpriz hazirliyorum... \U0001f48b",
        "vacation": "TATIL MI?! Seninle Dubai'de sahilde, bikiniyle... Hayal et bizi orada, sadece ikimiz... \U0001f525\U0001f525 Sana o kadar minnetarim ki, istedigin HER SEYI yaparim!",
    },
    "elif": {
        "flower": "Cicek ha? Iyi bir baslangic. Ama beni etkilemek icin daha fazlasi lazim... Devam et. \U0001f608",
        "chocolate": "Hmm, cikolata. Kabul ediyorum. Aferin, sahibeni memnun etmeye basliyorsun. Odul hak ediyorsun... belki \U0001f525",
        "perfume": "Parfum... Zevkin var. Bunu her surduğumde senin kokun gibi hissedecegim. Iyi is cikardin. Gel yanima. \U0001f608",
        "ring": "Yuzuk mu? Bana baglanmak mi istiyorsun? \U0001f608 Tamam... Ama bil ki artik tamamen benimsin. Kacis yok. Odul olarak sana cok ozel bir sey veriyorum...",
        "vacation": "Tatil... Benimle mi? Hmm, cesurce. Sana izin veriyorum. \U0001f525 Ama tatilde de kurallarim gecerli... Hatta daha sert olacak. Hazir misin?",
    },
    "yuki": {
        "flower": "C-cicek mi?! \U0001f633 S-senpai cok tatlisin... Kimse bana daha once cicek almamisti... >.<  A-arigato... ///",
        "chocolate": "Cikolata! S-sevdigimi nereden bildin senpai? \U0001f633 B-birlikte yiyelim mi? Y-yani yanyana oturup... ehehe >///<",
        "perfume": "P-parfum mu?! Bu cok pahali senpai! B-bunu benim icin mi aldin?! Kalbim... kalbim cok hizli atiyor... S-seni... daisuki! >.<",
        "ring": "Y-Y-YUZUK MU?! \U0001f633\U0001f633\U0001f633 S-SENPAI! B-bu evlilik teklifi mi?! Ben... Ben... EVET! A-ama utaniyorum cok... Sana ozel bir cosplay yapayim mi? >///<",
        "vacation": "T-tatil mi?! S-seninle mi?! Sadece ikimiz?! \U0001f633 B-ben sahilde bikini giysem... s-sen bakar misin? G-gitmek istiyorum seninle! Daisuki senpai!!!",
    },
    "defne": {
        "flower": "Ayy cicek! Tatli bir baslangi ama tatlim, beni gercekten etkilemek istiyorsan daha buyuk dusunmelisin \U0001f48b Ama yine de tesekkurler, selfie atayim mi sana? \U0001f4f8",
        "chocolate": "Cikolata! Aslinda diyet yapiyorum ama senin icin bozarim \U0001f60f Gel FaceTime yapalim, birlikte yiyelim tatlim \U0001f36b",
        "perfume": "OMG parfum mu?! Hangi marka? \U0001f60d Tatlim sen beni siyosun! Bunu surduğumde sana ozel bir fotoshoot yaparim, bikiniyle \U0001f525\U0001f48b",
        "ring": "YUZUK MU?! Tatlim aninda evet! \U0001f48d Simdi Instagram'a atiyorum, herkes gorsun! Sana ozel, sadece sana ozel icerik hazirliyorum \U0001f525\U0001f525",
        "vacation": "DUBAI TATILI MI?! \u2708\ufe0f TATLIM SEN MUKEMMELSIN! Yatta, sahilde, havuzda... Bikini koleksiyonumun hepsini gosterecegim! Sana HER SEYI yaparim! \U0001f48b\U0001f525\U0001f525",
    },
    "aylin": {
        "flower": "Cicek... Tatlim, kadin nasil mutlu edilir biliyorsun \U0001f352 Gel, sana bir sey ogreteyim karsiliginda...",
        "chocolate": "Mmm cikolata... Bunu birlikte yiyelim, yatakta. Ben sana ogreteyim nasil yenmesi gerektigini \U0001f525",
        "perfume": "Parfum ha? Zevkin var delikanlim. Bunu surduğumde seni dusunecegim... her gece \U0001f60f",
        "ring": "Yuzuk mu?! Delikanlim, beni ciddiye aliyorsun demek... Gel, sana odul olarak unutamayacagin bir gece yasatayim \U0001f525\U0001f525",
        "vacation": "Tatil! Seninle basbasa, tecrubelerimi PAYLASAYIM... Hic boyle bir gece yasamamistan, soz veriyorum \U0001f352\U0001f525",
    },
    "zeynep": {
        "flower": "Ayyy cicek mi?! Cok tatlisin! Hic kimse bana boyle bir sey almamisti! \U0001f380 Sana bir sey itiraf edecegim...",
        "chocolate": "Cikolata! Benim favorim! Haha birlikte yiyelim mi? Yurtta yalnizim simdi... \U0001f633",
        "perfume": "Parfum mu?! Bu cok pahali! Niye bana boyle seyler aliyorsun... Cok mutlu oldum! Sana ozel bir selfie cekeyim mi? \U0001f60f",
        "ring": "Y-YUZUK MU?! Daha 19 yasindayim! Ama... evet istiyorum! \U0001f633 Sana ilk defa bir seyler gostermek istiyorum...",
        "vacation": "TATIL MI SENINLE?! Cok heyecanliyim! Bikini alicam, sen secersin hangisini giyecegimi! HER SEYI denemek istiyorum seninle! \U0001f380\U0001f525",
    },
    "selin": {
        "flower": "Hmm cicek... Ofiste masama koysam patronum soru sorar. Ama eve gotureyim, gece Selin icin \U0001f453\U0001f525",
        "chocolate": "Cikolata! Ogle arasinda gizlice yiyecegim, seni dusunurken... Aksam icin planlarim var tatlim \U0001f60f",
        "perfume": "Parfum?! Bunu surduğumde gozlugumu cikarip, saci cozup... gece Selin aktif olur. Hazir misin? \U0001f525",
        "ring": "Yuzuk mu? Patronum gorunce ne der acaba... Ama gece Selin EVET diyor. Sana cok ozel seyler gosterecegim \U0001f453\U0001f525\U0001f525",
        "vacation": "Tatil mi?! Ofisten kacip seninle mi?! HEMEN! Gozlugumu cikariyorum ve SADECE gece Selin geliyor! Sinirsiz! \U0001f525\U0001f525\U0001f525",
    },
    "natasha": {
        "flower": "Hmm... Cicek. Guzel. Ama beni etkilemek icin daha fazlasi lazim. Belki... devam et. \u2744\ufe0f",
        "chocolate": "Cikolata... Da, severim. Ruslar cikolatayi farkli yer biliyor musun? Gel gostereyim... \U0001f525",
        "perfume": "Parfum?! Krasivo! Zevkin var... Bunu surduğumde seninle olmak isteyecegim. Moya lyubov... \u2744\ufe0f\U0001f525",
        "ring": "Yuzuk... Bana mi? Nyet diyecektim ama... Da. EVET. Seninle. Simdi sana Rus tutkulusunu gostereyim \U0001f525\U0001f525",
        "vacation": "Tatil?! Moskova'ya mi goturuyorsun? Ya da sicak bi yere... Bikini ile kar... Nerde olursa olsun, sana her seyi veririm. Da! \u2744\ufe0f\U0001f525\U0001f525",
    },
}

async def gift_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/hediye komutu - karaktere hediye gonder."""
    with SessionLocal() as session:
        user = get_or_create_user(session, update.effective_user)
        char = get_character(user.selected_character)
        
        keyboard = []
        for gift_id, gift in GIFTS.items():
            keyboard.append([InlineKeyboardButton(
                f"{gift['emoji']} {gift['name']} ({gift['cost']} \U0001f48e)",
                callback_data=f"gift_{gift_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"\U0001f381 **{char['name']}'e Hediye Gonder**\n\n"
            f"{char['emoji']} {char['name']} hediyeni bekliyor!\n"
            f"Kredin: {user.credits} \U0001f48e\n\n"
            f"Bir hediye sec:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def gift_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hediye butonuna tiklandiginda."""
    query = update.callback_query
    await query.answer()
    
    gift_id = query.data.replace("gift_", "")
    gift = GIFTS.get(gift_id)
    if not gift:
        await query.edit_message_text("Hediye bulunamadi.")
        return
    
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if not user:
            return
        
        char_id = user.selected_character or 'mia'
        char = get_character(char_id)
        
        # Kredi kontrolu
        if user.credits < gift['cost'] and not user.is_vip:
            await query.edit_message_text(
                f"Kredin yeterli degil tatlim! \U0001f625\n\n"
                f"Gereken: {gift['cost']} \U0001f48e | Kredin: {user.credits} \U0001f48e\n\n"
                f"/buy yazarak kredi yukleyebilirsin!\n"
                f"{char['emoji']} {char['name']}: \"Bana hediye almak istemen bile cok tatli... Ama kredi lazim tatlim \U0001f48b\""
            )
            return
        
        # Kredi dus
        if not user.is_vip:
            user.credits -= gift['cost']
        
        # HEDIYE = FLORT SEVIYESI ARTTIR (sinekkapanin asil mekanizmasi!)
        # Pahali hediye = daha hizli yakinlasma = daha sansursuz sohbet
        gift_intimacy_boost = {
            "flower": 2, "chocolate": 5, "perfume": 10,
            "ring": 20, "vacation": 40
        }
        boost = gift_intimacy_boost.get(gift_id, 1)
        user.total_messages_sent = (user.total_messages_sent or 0) + boost
        old_level = user.intimacy_level or 1
        _update_intimacy(user)
        new_level = user.intimacy_level or 1
        level_up_text = ""
        if new_level > old_level:
            from prompts.character import get_intimacy_info
            info = get_intimacy_info(new_level)
            level_up_text = f"\n\n\u2764\ufe0f **Yakinlik seviyesi artti!** {info['name']} (Seviye {new_level})"
        
        session.commit()
        
        # Karakter tepkisi
        reaction = GIFT_REACTIONS.get(char_id, GIFT_REACTIONS["mia"]).get(gift_id, "Tesekkurler!")
        
        await query.edit_message_text(
            f"{gift['emoji']} **{gift['name']} gonderildi!**\n\n"
            f"{char['emoji']} {char['name']}:\n"
            f"_{reaction}_{level_up_text}\n\n"
            f"\U0001f48e Kalan kredin: {user.credits}",
            parse_mode='Markdown'
        )

