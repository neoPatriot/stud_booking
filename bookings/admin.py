from django.contrib import admin
from .models import TimeSlot, Booking

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('room', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('room', 'date', 'status')
    search_fields = ('room__name',)
    date_hierarchy = 'date'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'timeslot', 'group_name', 'phone', 'status')
    list_filter = ('status', 'timeslot__room')
    search_fields = ('group_name', 'phone', 'email')
    raw_id_fields = ('timeslot', 'client')
