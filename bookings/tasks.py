from celery import shared_task
from django.utils import timezone
from .models import Booking


@shared_task
def send_reminder_emails():
    """Отправка напоминаний о бронировании за день до"""
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    bookings = Booking.objects.filter(
        timeslot__date=tomorrow,
        status='confirmed'
    )

    for booking in bookings:
        # Здесь будет логика отправки email
        print(f"Напоминание для брони #{booking.id} отправлено")

    return f"Отправлено {bookings.count()} напоминаний"
