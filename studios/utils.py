from datetime import datetime, timedelta
from django.utils import timezone
from .models import RoomSchedule, Room
from bookings.models import TimeSlot


def generate_timeslots(room, start_date, end_date):
    """
    Генерация таймслотов для зала на указанный период
    """
    schedules = RoomSchedule.objects.filter(room=room)
    current_date = start_date

    while current_date <= end_date:
        for schedule in schedules:
            if current_date.weekday() == schedule.day_of_week:
                time = schedule.start_time
                while True:
                    end_time = (datetime.combine(datetime.min, time) +
                                timedelta(minutes=schedule.slot_duration)).time()

                    if end_time > schedule.end_time:
                        break

                    TimeSlot.objects.get_or_create(
                        room=room,
                        date=current_date,
                        start_time=time,
                        end_time=end_time,
                        defaults={
                            'price': schedule.price,
                            'status': 'free'
                        }
                    )

                    time = end_time
        current_date += timedelta(days=1)


def generate_weekly_timeslots(room, weeks_ahead=4):
    """
    Генерация слотов на N недель вперёд
    """
    today = timezone.now().date()
    end_date = today + timedelta(weeks=weeks_ahead)
    generate_timeslots(room, today, end_date)