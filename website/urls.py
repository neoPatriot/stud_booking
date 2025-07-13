from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('rooms/', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('book/<int:slot_id>/', views.booking_form, name='booking_form'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]