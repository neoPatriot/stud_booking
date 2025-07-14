from django.db import models
from django.core.exceptions import ValidationError


class Studio(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    address = models.TextField(verbose_name="Адрес")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название зала")
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='rooms')
    description = models.TextField(blank=True, verbose_name="Описание")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.name} ({self.studio.name})"


class RoomSchedule(models.Model):
    DAY_CHOICES = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.PositiveIntegerField(
        default=60,
        help_text="Длительность слота в минутах"
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Расписание зала'
        verbose_name_plural = 'Расписания залов'
        unique_together = ('room', 'day_of_week')
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.room.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    def clean(self):
        if not hasattr(self, 'room'):
            return

        if self.start_time >= self.end_time:
            raise ValidationError("Время окончания должно быть позже времени начала")

        if self.slot_duration < 15:
            raise ValidationError("Минимальная длительность слота - 15 минут")

        overlapping = RoomSchedule.objects.filter(
            room=self.room,
            day_of_week=self.day_of_week,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Пересечение с существующим расписанием")