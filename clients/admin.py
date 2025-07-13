from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'telegram_chat_id')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_at',)
