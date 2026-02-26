import logging
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.models import SessionLocal, User, Transaction

logger = logging.getLogger(__name__)

# ============================================================
# ÖDEME SİSTEMİ
# Telegram Stars (yerleşik ödeme) + Test Modu + Kripto bilgi
# ============================================================

CREDIT_PACKAGES = [
    {"id": "pack_100", "credits": 100, "price": 50, "stars": 50, "label": "💎 100 Kredi"},
    {"id": "pack_500", "credits": 500, "price": 200, "stars": 200, "label": "💎 500 Kredi"},
    {"id": "pack_vip", "credits": 9999, "price": 500, "stars": 500, "label": "👑 VIP Sınırsız (Aylık)", "is_vip": True},
]

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcıya ödeme seçeneklerini gösterir."""
    keyboard = []
    for pkg in CREDIT_PACKAGES:
        keyboard.append([
            InlineKeyboardButton(
                f"{pkg['label']} - {pkg['price']} TL ({pkg['stars']}⭐)", 
                callback_data=f"buy_{pkg['id']}"
            )
        ])
    # Test modu butonu
    keyboard.append([InlineKeyboardButton("🧪 Test: Ücretsiz 50 Kredi", callback_data="buy_test_50")])
    # Kripto ödeme bilgi butonu
    keyboard.append([InlineKeyboardButton("₿ Kripto ile Öde", callback_data="buy_crypto_info")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💎 **Kredi Paketleri**\n\n"
        "Aşağıdaki paketlerden birini seçerek kredi yükleyebilirsin.\n"
        "Telegram Stars ⭐ ile ödeme yapabilirsin.\n\n"
        "💰 Metin mesajı: 1 kredi\n"
        "🎤 Sesli yanıt: 5 kredi\n"
        "📸 Fotoğraf: 10 kredi\n",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Satın alma butonlarına tıklama işleyicisi."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Kripto bilgi sayfası
    if data == "buy_crypto_info":
        await query.edit_message_text(
            "₿ **Kripto ile Ödeme**\n\n"
            "Aşağıdaki adrese USDT (TRC-20) göndererek kredi yükleyebilirsin:\n\n"
            "`TXXXXXXXXXXXXXXXXXXXXXXXXX`\n\n"
            "💡 Ödeme yaptıktan sonra işlem hash'ini bize ilet.\n"
            "Kredi 1 saat içinde hesabına yüklenir.\n\n"
            "⚠️ Minimum: 10 USDT (100 Kredi)",
            parse_mode='Markdown'
        )
        return
    
    # Test modu (ücretsiz kredi)
    if data == "buy_test_50":
        with SessionLocal() as session:
            user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
            if user:
                user.credits += 50
                tx = Transaction(user_id=user.id, amount=50, price_label="Test 50 Kredi", payment_method='test')
                session.add(tx)
                session.commit()
                await query.edit_message_text(
                    f"🧪 Test kredisi yüklendi!\n\n"
                    f"Hesabına 50 kredi eklendi.\n"
                    f"Toplam kredin: {user.credits} 💎\n\n"
                    f"Hadi sohbete devam edelim! 💬"
                )
        return
    
    # Telegram Stars ödeme akışı
    if data.startswith("buy_pack_"):
        pkg_id = data.replace("buy_", "")
        pkg = next((p for p in CREDIT_PACKAGES if p['id'] == pkg_id), None)
        
        if not pkg:
            await query.edit_message_text("Paket bulunamadı.")
            return
        
        # Telegram Stars ile ödeme faturası oluştur
        try:
            await context.bot.send_invoice(
                chat_id=update.effective_chat.id,
                title=pkg['label'],
                description=f"{pkg['credits']} kredi yükle ve sohbete devam et!",
                payload=f"credits_{pkg['credits']}_{pkg.get('is_vip', False)}",
                currency="XTR",  # Telegram Stars
                prices=[LabeledPrice(label=pkg['label'], amount=pkg['stars'])],
            )
            await query.edit_message_text(f"Ödeme faturası gönderildi! ⭐ Lütfen aşağıdaki faturayı onayla.")
        except Exception as e:
            logger.error(f"Invoice oluşturma hatası: {e}")
            # Fallback: Test modu gibi davran
            with SessionLocal() as session:
                user = session.query(User).filter(User.telegram_id == update.effective_user.id).first()
                if user:
                    user.credits += pkg['credits']
                    if pkg.get('is_vip'):
                        user.is_vip = True
                    tx = Transaction(user_id=user.id, amount=pkg['credits'], price_label=pkg['label'], payment_method='test')
                    session.add(tx)
                    session.commit()
                    await query.edit_message_text(
                        f"🎉 Tebrikler! {pkg['credits']} kredi yüklendi!\n"
                        f"Toplam kredin: {user.credits} 💎\n\n"
                        f"{'👑 VIP üyeliğin aktif!' if pkg.get('is_vip') else ''}"
                    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram Stars ödeme onayı (pre-checkout query)."""
    query = update.pre_checkout_query
    # Tüm ödemeleri onayla
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram Stars ödeme başarılı olduğunda kredi yükle."""
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    
    # payload formatı: "credits_100_False" veya "credits_9999_True"
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
            
            await update.message.reply_text(
                f"🎉 Ödeme başarılı! Teşekkürler!\n\n"
                f"💎 {credits_amount} kredi hesabına yüklendi.\n"
                f"Toplam kredin: {user.credits} 💎\n"
                f"{'👑 VIP üyeliğin aktif edildi!' if is_vip else ''}\n\n"
                f"Hadi sohbete devam edelim! 💬"
            )
    
    logger.info(f"Başarılı ödeme: user={update.effective_user.id}, credits={credits_amount}, vip={is_vip}")
