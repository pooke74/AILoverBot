from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import func
from datetime import datetime, date
from database.models import SessionLocal, User, Transaction, Message
from config import ADMIN_TELEGRAM_ID

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin ozel istatistik komutu."""
    if str(update.effective_user.id) != str(ADMIN_TELEGRAM_ID):
        await update.message.reply_text("Bu komutu kullanmaya yetkiniz yok.")
        return
        
    with SessionLocal() as session:
        # Genel Istatistikler
        total_users = session.query(User).count()
        total_messages = session.query(Message).count()
        total_revenue = session.query(func.sum(Transaction.amount)).filter(Transaction.payment_method == 'stars').scalar() or 0
        
        # Bugunku istatistikler
        today_start = datetime.combine(date.today(), datetime.min.time())
        today_users = session.query(User).filter(User.created_at >= today_start).count()
        today_revenue = session.query(func.sum(Transaction.amount)).filter(Transaction.created_at >= today_start, Transaction.payment_method == 'stars').scalar() or 0
        
        # VIP Kullanicilar
        vip_users = session.query(User).filter(User.is_vip == True).count()
        
        msg = (
            f"📊 *Günlük Özet - AILoverBot*\n\n"
            f"👥 *Toplam Kullanıcı:* {total_users}\n"
            f"📈 *Bugün Katılan:* +{today_users}\n\n"
            f"💬 *Toplam Mesaj:* {total_messages}\n"
            f"👑 *VIP Üyeler:* {vip_users}\n\n"
            f"💰 *Toplam Harcanan Stars (Kredi):* {total_revenue}\n"
            f"🪙 *Bugünkü Gelir (Stars):* {today_revenue}\n"
        )
        
        await update.message.reply_text(msg, parse_mode='Markdown')
