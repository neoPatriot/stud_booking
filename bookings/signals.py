from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from telegram_bots.admin_bot import send_telegram_notification

@receiver(post_save, sender=Booking)
def booking_created(sender, instance, created, **kwargs):
    if created:
        # Отправляем уведомление в Telegram о новой брони
        message = (
            f"🎸 Новая бронь!\n"
            f"ID: #{instance.id}\n"
            f"Зал: {instance.timeslot.room.name}\n"
            f"Дата: {instance.timeslot.date}\n"
            f"Время: {instance.timeslot.start_time}-{instance.timeslot.end_time}\n"
            f"Группа: {instance.group_name or '-'}\n"
            f"Телефон: {instance.phone}"
        )
        send_telegram_notification(message)
