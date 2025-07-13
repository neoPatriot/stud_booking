import json  # Добавьте эту строку в начало файла
from django.db import models


class Studio(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название студии")
    description = models.TextField(verbose_name="Описание", blank=True)
    contact_phone = models.CharField(max_length=20, verbose_name="Телефон")
    contact_email = models.EmailField(verbose_name="Email")
    logo = models.ImageField(upload_to='studios/logo/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=255, verbose_name="Название зала")
    description = models.TextField(verbose_name="Описание", blank=True)
    equipment = models.JSONField(default=dict, verbose_name="Оборудование")
    area = models.PositiveIntegerField(verbose_name="Площадь (м²)", default=0)
    slot_duration = models.PositiveIntegerField(
        default=60,
        verbose_name="Длительность слота (мин)",
        help_text="Длительность одного временного интервала в минутах"
    )
    price_per_slot = models.DecimalField(
        verbose_name="Стоимость слота",
        max_digits=8,
        decimal_places=2,
        default=1000.00,
        help_text="Базовая стоимость одного временного слота"
    )
    photo = models.ImageField(upload_to='rooms/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.studio.name})"

    def equipment_display(self):
        if not self.equipment:
            return ""

        # Если equipment уже словарь - используем как есть
        if isinstance(self.equipment, dict):
            equipment = self.equipment
        else:
            try:
                # Если это строка - пробуем декодировать JSON
                equipment = json.loads(self.equipment)
            except (json.JSONDecodeError, TypeError):
                return str(self.equipment)

        return ", ".join([f"{item} - {qty} шт." for item, qty in equipment.items()])


class RoomSchedule(models.Model):
    DAYS_OF_WEEK = (
        ('mon', 'Понедельник'),
        ('tue', 'Вторник'),
        ('wed', 'Среда'),
        ('thu', 'Четверг'),
        ('fri', 'Пятница'),
        ('sat', 'Суббота'),
        ('sun', 'Воскресенье'),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK, verbose_name="День недели")
    start_time = models.TimeField(verbose_name="Начало работы")
    end_time = models.TimeField(verbose_name="Окончание работы")
    is_active = models.BooleanField(default=True, verbose_name="Активно")

    class Meta:
        unique_together = ('room', 'day_of_week')
        ordering = ['room', 'day_of_week']

    def __str__(self):
        return f"{self.room}: {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"