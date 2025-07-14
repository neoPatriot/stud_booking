from django.db import models
from studios.models import Room
from clients.models import Client

class TimeSlot(models.Model):
    STATUS_CHOICES = (
        ('free', 'Свободен'),
        ('booked', 'Забронирован'),
        ('blocked', 'Заблокирован'),
    )

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='timeslots')
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Начало слота")
    end_time = models.TimeField(verbose_name="Конец слота")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Таймслот"
        verbose_name_plural = "Таймслоты"
        unique_together = ('room', 'date', 'start_time')
        indexes = [
            models.Index(fields=['room', 'date', 'status']),
        ]
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.room} - {self.date} {self.start_time}-{self.end_time} ({self.status})"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
    )

    timeslot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='booking')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='bookings')
    group_name = models.CharField(max_length=100, blank=True, verbose_name="Название группы")
    phone = models.CharField(max_length=20, verbose_name="Телефон для связи")
    email = models.EmailField(verbose_name="Email")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']

    def __str__(self):
        return f"Бронь #{self.id} ({self.timeslot})"