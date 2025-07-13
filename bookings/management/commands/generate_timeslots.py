from django.core.management.base import BaseCommand
from django.utils import timezone
from studios.models import Room, RoomSchedule
from bookings.models import TimeSlot
from datetime import datetime, timedelta, time
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Генерация временных слотов с сохранением существующих броней'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=14,
            help='Количество дней для генерации слотов (по умолчанию 14)',
        )

    def handle(self, *args, **options):
        days_ahead = options['days_ahead']
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days_ahead)

        for room in Room.objects.select_related('studio'):
            self.process_room(room, start_date, end_date)

        self.stdout.write(self.style.SUCCESS(f"Генерация завершена. Созданы слоты до {end_date}"))

    def process_room(self, room, start_date, end_date):
        self.stdout.write(f"\nОбработка зала: {room.name}")

        if not hasattr(room, 'slot_duration') or not room.slot_duration:
            self.stdout.write(self.style.ERROR("✖ Не указана длительность слота!"))
            return

        schedules = RoomSchedule.objects.filter(room=room, is_active=True)
        if not schedules.exists():
            self.stdout.write(self.style.WARNING("⚠ Нет активного расписания!"))
            return

        for single_date in self.date_range(start_date, end_date):
            self.process_date(room, single_date, schedules)

    def process_date(self, room, date, schedules):
        day_name = date.strftime('%a').lower()
        day_schedules = schedules.filter(day_of_week=day_name)

        if not day_schedules.exists():
            return

        for schedule in day_schedules:
            self.generate_slots(room, date, schedule)

    def generate_slots(self, room, date, schedule):
        slot_duration = room.slot_duration
        current_datetime = datetime.combine(date, schedule.start_time)
        end_datetime = datetime.combine(date, schedule.end_time)

        if schedule.end_time == time(0, 0):
            end_datetime += timedelta(days=1)

        while current_datetime < end_datetime:
            slot_end = current_datetime + timedelta(minutes=slot_duration)

            if slot_end > end_datetime:
                slot_end = end_datetime

            slot_start_time = current_datetime.time()
            slot_end_time = slot_end.time()

            if slot_start_time >= slot_end_time:
                break

            # Проверяем существование слота
            existing_slot = TimeSlot.objects.filter(
                room=room,
                date=date,
                start_time=slot_start_time
            ).first()

            if existing_slot:
                # Не изменяем статус существующего слота
                self.stdout.write(
                    f"  Сохранен существующий слот: {date} {slot_start_time}-{existing_slot.end_time} (статус: {existing_slot.status})")
            else:
                # Создаем новый свободный слот с ценой из зала
                TimeSlot.objects.create(
                    room=room,
                    date=date,
                    start_time=slot_start_time,
                    end_time=slot_end_time,
                    status='free',
                    price=room.price_per_slot  # Используем стоимость из зала
                )
                self.stdout.write(
                    f"  Создан новый слот: {date} {slot_start_time}-{slot_end_time} (цена: {room.price_per_slot} руб.)")

            current_datetime = slot_end

    @staticmethod
    def date_range(start_date, end_date):
        for n in range((end_date - start_date).days + 1):
            yield start_date + timedelta(days=n)