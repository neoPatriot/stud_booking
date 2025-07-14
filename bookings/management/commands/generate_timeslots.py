from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, time, timedelta
from studios.models import Room, RoomSchedule
from bookings.models import TimeSlot


class Command(BaseCommand):
    help = 'Генерация таймслотов для всех залов на указанное количество дней вперед'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=14,
            help='Количество дней для генерации (по умолчанию: 14)'
        )
        parser.add_argument(
            '--room-id',
            type=int,
            help='ID конкретного зала для генерации'
        )

    def handle(self, *args, **options):
        days_ahead = options['days_ahead']
        room_id = options.get('room_id')
        today = timezone.now().date()
        end_date = today + timedelta(days=days_ahead)

        # Получаем залы для обработки
        rooms = self.get_rooms_to_process(room_id)
        if not rooms:
            return

        total_created = 0

        for room in rooms:
            created = self.generate_room_timeslots(room, today, end_date)
            total_created += created
            self.stdout.write(
                self.style.SUCCESS(f'Создано {created} таймслотов для зала {room.name}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Готово! Всего создано {total_created} таймслотов до {end_date}')
        )

    def get_rooms_to_process(self, room_id):
        if room_id:
            rooms = Room.objects.filter(id=room_id, is_active=True)
            if not rooms.exists():
                self.stdout.write(self.style.ERROR(f'Зал с ID {room_id} не найден или неактивен'))
                return None
        else:
            rooms = Room.objects.filter(is_active=True)
            if not rooms.exists():
                self.stdout.write(self.style.WARNING('Нет активных залов для генерации'))
                return None
        return rooms

    def generate_room_timeslots(self, room, start_date, end_date):
        schedules = RoomSchedule.objects.filter(room=room)
        if not schedules.exists():
            self.stdout.write(self.style.WARNING(f'Для зала {room.name} не задано расписание!'))
            return 0

        created_count = 0
        current_date = start_date

        while current_date <= end_date:
            for schedule in schedules:
                if current_date.weekday() == schedule.day_of_week:
                    created_count += self.generate_day_timeslots(room, current_date, schedule)
            current_date += timedelta(days=1)

        return created_count

    def generate_day_timeslots(self, room, date, schedule):
        created = 0
        current_time = schedule.start_time

        while True:
            # Вычисляем время окончания слота
            end_time = self.calculate_end_time(current_time, schedule.slot_duration)
            if end_time > schedule.end_time:
                break

            # Создаем таймслот если его еще нет
            _, is_created = TimeSlot.objects.get_or_create(
                room=room,
                date=date,
                start_time=current_time,
                defaults={
                    'end_time': end_time,
                    'price': schedule.price,
                    'status': 'free'
                }
            )

            if is_created:
                created += 1

            current_time = end_time

        return created

    def calculate_end_time(self, start_time, duration_minutes):
        """Вычисляет время окончания слота"""
        dummy_date = datetime(2000, 1, 1)  # Фиктивная дата для вычислений
        start_dt = datetime.combine(dummy_date, start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        return end_dt.time()