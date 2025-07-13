from django.shortcuts import render, get_object_or_404, redirect
from studios.models import Room
from bookings.models import TimeSlot
from clients.models import Client
from bookings.models import Booking
from django.utils import timezone


def index(request):
    return render(request, 'website/index.html')


def room_list(request):
    rooms = Room.objects.all().select_related('studio')
    return render(request, 'website/room_list.html', {'rooms': rooms})


def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    # Получаем свободные слоты на ближайшие 7 дней
    start_date = timezone.now().date()
    end_date = start_date + timezone.timedelta(days=7)

    available_slots = TimeSlot.objects.filter(
        room=room,
        date__range=[start_date, end_date],
        status='free'
    ).order_by('date', 'start_time')

    return render(request, 'website/room_detail.html', {
        'room': room,
        'available_slots': available_slots
    })


def booking_form(request, slot_id):
    timeslot = get_object_or_404(TimeSlot, id=slot_id, status='free')

    if request.method == 'POST':
        # Создаем клиента или находим существующего
        client, created = Client.objects.get_or_create(
            phone=request.POST['phone'],
            defaults={
                'name': request.POST['name'],
                'email': request.POST.get('email', '')
            }
        )

        # Создаем бронирование
        booking = Booking.objects.create(
            timeslot=timeslot,
            client=client,
            group_name=request.POST.get('group_name', ''),
            phone=request.POST['phone'],
            email=request.POST.get('email', ''),
            comment=request.POST.get('comment', '')
        )

        # Обновляем статус слота
        timeslot.status = 'booked'
        timeslot.save()

        return render(request, 'website/booking_success.html', {'booking': booking})

    return render(request, 'website/booking.html', {'timeslot': timeslot, 'room': timeslot.room})


def my_bookings(request):
    phone = request.GET.get('phone')
    bookings = []

    if phone:
        try:
            client = Client.objects.get(phone=phone)
            bookings = client.bookings.all().order_by('-timeslot__date', '-timeslot__start_time')
        except Client.DoesNotExist:
            pass

    return render(request, 'website/my_bookings.html', {
        'bookings': bookings,
        'phone': phone or ''
    })