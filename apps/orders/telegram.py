import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_order_notification(order):
    """Yangi buyurtma haqida Telegram ga xabar yuborish"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')

    if not token or not chat_id:
        return

    items_text = '\n'.join(
        f"  • {item.curtain.title} x{item.quantity} — {item.get_total_price():,} so'm"
        for item in order.items.select_related('curtain').all()
    )

    text = (
        f"🛒 Yangi buyurtma #{order.order_number}\n\n"
        f"👤 Mijoz: {order.customer_name}\n"
        f"📞 Telefon: {order.customer_phone}\n"
        f"📍 Manzil: {order.customer_address}\n\n"
        f"📦 Mahsulotlar:\n{items_text}\n\n"
        f"💰 Jami: {order.get_total_amount():,} so'm"
    )
    if order.notes:
        text += f"\n\n📝 Izoh: {order.notes}"

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Telegram xabar yuborishda xatolik: %s", e)
