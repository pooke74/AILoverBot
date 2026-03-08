import logging
from datetime import datetime
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import SessionLocal, User, Transaction
from prompts.character import get_character

logger = logging.getLogger(__name__)

# ============================================================
# ODEME SISTEMI v2.0
# Telegram Stars + Test Modu + Kripto + VIP Abonelik
# ============================================================

CREDIT_PACKAGES = [
    {"id": "pack_50",   "credits": 50,   "stars": 25,   "label": "\U0001f48e 50 Kredi",   "desc": "~50 mesaj"},
    {"id": "pack_200",  "credits": 200,  "stars": 75,   "label": "\U0001f48e 200 Kredi",  "desc": "~200 mesaj veya 20 fotograf"},
    {"id": "pack_500",  "credits": 500,  "stars": 150,  "label": "\U0001f48e 500 Kredi",  "desc": "~500 mesaj veya 50 fotograf", "popular": True},
    {"id": "pack_vip_weekly",  "credits": 9999, "stars": 100,  "label": "\U0001f451 VIP Haftalik",  "desc": "7 gun sinirsiz", "is_vip": True},
    {"id": "pack_vip_monthly", "credits": 9999, "stars": 300,  "label": "\U0001f451 VIP Aylik",    "desc": "30 gun sinirsiz", "is_vip": True},
]

# Basarili odeme sonrasi karakter tepkileri
PAYMENT_REACTIONS = {
    "mia": "Ayyy cok tatlisin! Benim icin harcama yaptin, cok mutlu oldum! Gel sana ozel bir seyler gostereyim \U0001f618",
    "elif": "Hmm, aferin. Boyle devam et, odul hak ediyorsun \U0001f608",
    "yuki": "S-sagol... Cok dusuncelisin senpai! B-bunu beklemiyordum >.<",
    "defne": "Ay cok sukur ya! Artik seninle daha fazla vakit gecirebilirim \U0001f48b Beni yemege de cikarirsin artik!",
}

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullaniciya odeme seceneklerini gosterir."""
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        current_credits = user.credits if user else 0
    
    keyboard = []
    for pkg in CREDIT_PACKAGES:
        popular = " \u2b50 EN POPULER" if pkg.get("popular") else ""
        label = f"{pkg['label']} - {pkg['stars']}\u2b50{popular}"
        keyboard.append([InlineKeyboardButton(label, callback_data=f"buy_{pkg['id']}")])
    
    from config import ADMIN_TELEGRAM_ID
    if str(update.effective_user.id) == str(ADMIN_TELEGRAM_ID):
        keyboard.append([InlineKeyboardButton("🧪 Test: Ücretsiz 50 Kredi (Admin)", callback_data="buy_test_50")])
        
    keyboard.append([InlineKeyboardButton("₿ Kripto ile Öde (USDT)", callback_data="buy_crypto_info")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "\U0001f48e **Kredi Yukle**\n\n"
        f"Mevcut kredin: {current_credits} \U0001f48e\n\n"
        "\u270f Mesaj: 1 kredi\n"
        "\U0001f3a4 Sesli yanit: 5 kredi\n"
        "\U0001f4f8 Fotograf: 10 kredi\n\n"
        "\U0001f451 **VIP Avantajlari:**\n"
        "\u2022 Sinirsiz mesaj, ses ve fotograf\n"
        "\u2022 Oncelikli destek\n"
        "\u2022 Ozel icerikler\n",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Satin alma butonlarina tiklama isleyicisi."""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # Kripto bilgi sayfasi
    if data == "buy_crypto_info":
        keyboard = [[InlineKeyboardButton("\u25c0 Geri", callback_data="buy_back")]]
        await query.edit_message_text(
            "\u20bf **Kripto ile Odeme**\n\n"
            "Asagidaki adrese USDT (TRC-20) gonder:\n\n"
            "`TXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
            "\U0001f4b0 **Fiyatlar:**\n"
            "\u2022 10 USDT = 200 Kredi\n"
            "\u2022 25 USDT = 600 Kredi (bonus!)\n"
            "\u2022 50 USDT = VIP 3 Ay\n\n"
            "Odeme yaptiktan sonra islem hash'ini @destek_hesabi adresine ilet.\n"
            "Kredin 1 saat icinde yuklenir.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # Test modu (ucretsiz kredi)
    if data == "buy_test_50":
        from config import ADMIN_TELEGRAM_ID
        if str(update.effective_user.id) != str(ADMIN_TELEGRAM_ID):
            await query.answer("Bu buton sadece admin içindir!", show_alert=True)
            return
            
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            if user:
                user.credits += 50
                tx = Transaction(user_id=user.id, amount=50, price_label="Test 50 Kredi", payment_method='test')
                session.add(tx)
                session.commit()
                
                char = get_character(user.selected_character)
                await query.edit_message_text(
                    f"\U0001f9ea Test kredisi yuklendi!\n\n"
                    f"\U0001f48e +50 kredi eklendi\n"
                    f"Toplam kredin: {user.credits} \U0001f48e\n\n"
                    f"{char['emoji']} {char['name']}: \"{PAYMENT_REACTIONS.get(user.selected_character, 'Tesekkurler!')}\""
                )
                from utils import send_admin_alert
                await send_admin_alert(
                    context,
                    f"🔬 *Test Kredisi Alındı!*\n👤 Kullanıcı: {user.first_name} (`{user.telegram_id}`)\n💎 Miktar: 50 Kredi"
                )
        return
    
    # Geri butonu
    if data == "buy_back":
        # buy_command'in icerigini tekrar goster
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            current_credits = user.credits if user else 0
        
        keyboard = []
        for pkg in CREDIT_PACKAGES:
            popular = " \u2b50 EN POPULER" if pkg.get("popular") else ""
            label = f"{pkg['label']} - {pkg['stars']}\u2b50{popular}"
            keyboard.append([InlineKeyboardButton(label, callback_data=f"buy_{pkg['id']}")])
            
        from config import ADMIN_TELEGRAM_ID
        if str(update.effective_user.id) == str(ADMIN_TELEGRAM_ID):
            keyboard.append([InlineKeyboardButton("🧪 Test: Ücretsiz 50 Kredi (Sadece Admin)", callback_data="buy_test_50")])
            
        keyboard.append([InlineKeyboardButton("₿ Kripto ile Öde (USDT)", callback_data="buy_crypto_info")])
        
        await query.edit_message_text(
            "\U0001f48e **Kredi Yukle**\n\n"
            f"Mevcut kredin: {current_credits} \U0001f48e\n\n"
            "\u270f Mesaj: 1 kredi | \U0001f3a4 Ses: 5 | \U0001f4f8 Foto: 10\n\n"
            "\U0001f451 VIP = Sinirsiz her sey!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    # Telegram Stars odeme akisi
    if data.startswith("buy_pack_"):
        pkg_id = data.replace("buy_", "")
        pkg = next((p for p in CREDIT_PACKAGES if p['id'] == pkg_id), None)
        
        if not pkg:
            await query.edit_message_text("Paket bulunamadi.")
            return
        
        try:
            await context.bot.send_invoice(
                chat_id=update.effective_chat.id,
                title=pkg['label'],
                description=f"{pkg['desc']} - {pkg['credits']} kredi yukle!",
                payload=f"credits_{pkg['credits']}_{pkg.get('is_vip', False)}",
                currency="XTR",
                prices=[LabeledPrice(label=pkg['label'], amount=pkg['stars'])],
            )
            await query.edit_message_text(f"Odeme faturasi gonderildi! \u2b50 Asagidaki faturayi onayla.")
        except Exception as e:
            logger.error(f"Invoice olusturma hatasi: {e}")
            # Fallback: Test modu
            with SessionLocal() as session:
                user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
                if user:
                    user.credits += pkg['credits']
                    if pkg.get('is_vip'):
                        user.is_vip = True
                    tx = Transaction(user_id=user.id, amount=pkg['credits'], price_label=pkg['label'], payment_method='test_fallback')
                    session.add(tx)
                    session.commit()
                    
                    char = get_character(user.selected_character)
                    vip_text = "\n\U0001f451 VIP uyeligin aktif!" if pkg.get('is_vip') else ""
                    await query.edit_message_text(
                        f"\U0001f389 {pkg['credits']} kredi yuklendi!{vip_text}\n"
                        f"Toplam kredin: {user.credits} \U0001f48e\n\n"
                        f"{char['emoji']} {char['name']}: \"{PAYMENT_REACTIONS.get(user.selected_character, 'Tesekkurler!')}\""
                    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram Stars odeme onayi."""
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram Stars odeme basarili oldugunda kredi yukle."""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    
    parts = payload.split("_")
    credits_amount = int(parts[1])
    is_vip = parts[2] == "True"
    
    with SessionLocal() as session:
        user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
        if user:
            user.credits += credits_amount
            if is_vip:
                user.is_vip = True
            
            tx = Transaction(
                user_id=user.id,
                amount=credits_amount,
                price_label=f"{credits_amount} Kredi (Stars)",
                payment_method='stars',
                telegram_payment_id=payment.telegram_payment_charge_id
            )
            session.add(tx)
            session.commit()
            
            char = get_character(user.selected_character)
            reaction = PAYMENT_REACTIONS.get(user.selected_character, "Tesekkurler!")
            vip_text = "\n\U0001f451 VIP uyeligin aktif edildi!" if is_vip else ""
            
            await update.message.reply_text(
                f"\U0001f389 **Odeme basarili!** Tesekkurler!\n\n"
                f"\U0001f48e +{credits_amount} kredi yuklendi{vip_text}\n"
                f"Toplam kredin: {user.credits} \U0001f48e\n\n"
                f"{char['emoji']} _{reaction}_",
                parse_mode='Markdown'
            )
            
            from utils import send_admin_alert
            await send_admin_alert(
                context,
                f"💰 *Yeni Ödeme Alındı!* (Stars)\n👤 Kullanıcı: {user.first_name} (`{user.telegram_id}`)\n💎 Miktar: {credits_amount} Kredi"
            )
    
    logger.info(f"Basarili odeme: user={update.effective_user.id}, credits={credits_amount}, vip={is_vip}")
