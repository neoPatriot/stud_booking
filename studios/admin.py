from django.contrib import admin
from .models import Studio, Room, RoomSchedule


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'studio', 'is_active')
    list_filter = ('studio', 'is_active')
    search_fields = ('name', 'studio__name')


@admin.register(RoomSchedule)
class RoomScheduleAdmin(admin.ModelAdmin):
    list_display = ('room', 'get_day_of_week_display', 'start_time', 'end_time', 'price')
    list_filter = ('room__studio', 'room', 'day_of_week')
    fieldsets = (
        (None, {
            'fields': ('room', 'day_of_week')
        }),
        ('Расписание', {
            'fields': ('start_time', 'end_time', 'slot_duration', 'price')
        })
    )

    actions = ['generate_timeslots']

    def generate_timeslots(self, request, queryset):
        for schedule in queryset:
            from studios.utils import generate_weekly_timeslots
            generate_weekly_timeslots(schedule.room)
        self.message_user(request, "Таймслоты успешно сгенерированы")

    generate_timeslots.short_description = "Сгенерировать таймслоты на 4 недели"