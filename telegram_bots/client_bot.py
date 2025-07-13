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

# Состояния для FSM
SELECT_ROOM, SELECT_DATE, SELECT_SLOT, ENTER_NAME, ENTER_PHONE = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Привет! Я помогу тебе забронировать зал для репетиции.\n"
        "Используй команды:\n"
        "/book - Начать бронирование\n"
        "/mybookings - Мои бронирования"
    )


async def book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rooms = Room.objects.all()
    if not rooms:
        await update.message.reply_text("Извините, в данный момент нет доступных залов.")
        return ConversationHandler.END

    keyboard = []
    for room in rooms:
        keyboard.append([InlineKeyboardButton(room.name, callback_data=f"room_{room.id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите зал для бронирования:", reply_markup=reply_markup)

    return SELECT_ROOM


async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    room_id = int(query.data.split("_")[1])
    context.user_data['room_id'] = room_id

    # Кнопки для выбора даты
    today = timezone.now().date()
    dates = [
        today,
        today + datetime.timedelta(days=1),
        today + datetime.timedelta(days=2),
        today + datetime.timedelta(days=3),
        today + datetime.timedelta(days=4),
    ]

    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(date.strftime("%d.%m.%Y"), callback_data=f"date_{date}")])

    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выберите дату:", reply_markup=reply_markup)

    return SELECT_DATE


async def select_slot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_date = datetime.datetime.strptime(query.data.split("_")[1], "%Y-%m-%d").date()
    context.user_data['selected_date'] = selected_date

    room_id = context.user_data['room_id']
    room = Room.objects.get(id=room_id)

    # Получаем доступные слоты
    slots = TimeSlot.objects.filter(
        room=room,
        date=selected_date,
        status='free'
    ).order_by('start_time')

    if not slots:
        await query.edit_message_text("На выбранную дату нет свободных слотов. Попробуйте другую дату.")
        return ConversationHandler.END

    keyboard = []
    for slot in slots:
        time_str = f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}"
        keyboard.append([InlineKeyboardButton(time_str, callback_data=f"slot_{slot.id}")])

    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Выберите время для {room.name} на {selected_date.strftime('%d.%m.%Y')}:",
                                  reply_markup=reply_markup)

    return SELECT_SLOT


async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    slot_id = int(query.data.split("_")[1])
    context.user_data['slot_id'] = slot_id

    await query.edit_message_text("Введите ваше имя или название группы:")
    return ENTER_NAME


async def enter_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Введите ваш телефон для связи:")
    return ENTER_PHONE


async def complete_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    name = context.user_data['name']
    slot_id = context.user_data['slot_id']

    slot = TimeSlot.objects.get(id=slot_id)

    # Создаем клиента
    client, created = Client.objects.get_or_create(
        phone=phone,
        defaults={'name': name}
    )

    # Создаем бронирование
    booking = Booking.objects.create(
        timeslot=slot,
        client=client,
        group_name=name,
        phone=phone,
        status='pending'
    )

    # Обновляем статус слота
    slot.status = 'booked'
    slot.save()

    await update.message.reply_text(
        f"✅ Бронь успешно создана!\n"
        f"Зал: {slot.room.name}\n"
        f"Дата: {slot.date.strftime('%d.%m.%Y')}\n"
        f"Время: {slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}\n"
        f"Номер брони: #{booking.id}\n\n"
        f"Администратор свяжется с вами для подтверждения."
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Бронирование отменено.")
    return ConversationHandler.END


async def my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь будет реализация просмотра бронирований
    await update.message.reply_text("Функция просмотра бронирований в разработке.")


def main():
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("Telegram bot token not configured")
        return

    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик команды /mybookings
    application.add_handler(CommandHandler("mybookings", my_bookings))

    # Обработчик процесса бронирования
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('book', book_start)],
        states={
            SELECT_ROOM: [CallbackQueryHandler(select_date, pattern='^room_')],
            SELECT_DATE: [CallbackQueryHandler(select_slot, pattern='^date_')],
            SELECT_SLOT: [CallbackQueryHandler(enter_name, pattern='^slot_')],
            ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_phone)],
            ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_booking)],
        },
        fallbacks=[CallbackQueryHandler(cancel, pattern='^cancel$')],
    )

    application.add_handler(conv_handler)

    logger.info("Client bot started")
    application.run_polling()


if __name__ == "__main__":
    main()