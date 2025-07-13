import json  # Добавьте эту строку в начало файла
from django import forms
from django.contrib import admin
from .models import Studio, Room, RoomSchedule
from .widgets import EquipmentWidget


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        help_texts = {
            'price_per_slot': 'Базовая стоимость бронирования одного временного интервала',
        }
        widgets = {
            'equipment': EquipmentWidget,
        }


class RoomScheduleForm(forms.ModelForm):
    class Meta:
        model = RoomSchedule
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Время окончания должно быть позже времени начала")

        return cleaned_data


class RoomScheduleInline(admin.TabularInline):
    model = RoomSchedule
    form = RoomScheduleForm
    extra = 0
    fields = ('day_of_week', 'start_time', 'end_time', 'is_active')
    min_num = 1
    verbose_name = "Расписание"
    verbose_name_plural = "Расписания работы"


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_phone', 'contact_email')
    search_fields = ('name', 'contact_phone')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomForm
    list_display = ('name', 'studio', 'slot_duration', 'price_per_slot', 'area', 'equipment_display')
    list_filter = ('studio',)
    search_fields = ('name', 'description')
    raw_id_fields = ('studio',)
    inlines = [RoomScheduleInline]

    fieldsets = [
        ('Основная информация', {
            'fields': ('name', 'studio', 'description', 'photo')
        }),
        ('Характеристики', {
            'fields': ('area', 'slot_duration', 'price_per_slot', 'equipment'),
            'description': 'Технические параметры зала'
        }),
    ]

    def equipment_display(self, obj):
        return obj.equipment_display()

    equipment_display.short_description = "Оборудование"


@admin.register(RoomSchedule)
class RoomScheduleAdmin(admin.ModelAdmin):
    list_display = ('room', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('room__studio', 'day_of_week', 'is_active')
    raw_id_fields = ('room',)