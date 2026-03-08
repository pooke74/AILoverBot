import logging
from config import ADMIN_TELEGRAM_ID

async def send_admin_alert(context, message: str):
    if not ADMIN_TELEGRAM_ID:
        return
    try:
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_ID,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"Admin bildirim hatasi: {e}")
