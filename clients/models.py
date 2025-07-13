from django.db import models

class Client(models.Model):
    telegram_chat_id = models.BigIntegerField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    def __str__(self):
        return f"{self.name} ({self.phone})"