import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
from studios.models import Room
from bookings.models import TimeSlot, Booking  # Импорт из правильного приложения
from clients.models import Client
import datetime
import logging
from django.utils import timezone

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def send_telegram_notification(message):
    """Отправка сообщения в административный чат"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_ADMIN_CHAT_ID:
        logger.error("Telegram token or chat ID not configured")
        return

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.bot.send_message(chat_id=settings.TELEGRAM_ADMIN_CHAT_ID, text=message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот для администраторов студии.")


async def today_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = timezone.now().date()
    bookings = Booking.objects.filter(timeslot__date=today).select_related('timeslot__room')

    if not bookings:
        await update.message.reply_text("На сегодня броней нет.")
        return

    message = "🎸 Брони на сегодня:\n\n"
    for booking in bookings:
        message += (
            f"#{booking.id} {booking.timeslot.room.name}\n"
            f"⏰ {booking.timeslot.start_time.strftime('%H:%M')}-{booking.timeslot.end_time.strftime('%H:%M')}\n"
            f"👤 {booking.group_name or booking.client.name}\n"
            f"📞 {booking.phone}\n"
            f"🔹 Статус: {booking.get_status_display()}\n\n"
        )
    await update.message.reply_text(message)


async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        booking_id = context.args[0]
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'confirmed'
        booking.save()

        # Обновляем статус слота
        booking.timeslot.status = 'booked'
        booking.timeslot.save()

        await update.message.reply_text(f"✅ Бронь #{booking_id} подтверждена!")
    except (IndexError, Booking.DoesNotExist):
        await update.message.reply_text("❌ Укажите ID существующей брони.")


def main():
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not configured")
        return

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today_bookings))
    application.add_handler(CommandHandler("confirm", confirm_booking))

    logger.info("Admin bot started")
    application.run_polling()


if __name__ == "__main__":
    main()