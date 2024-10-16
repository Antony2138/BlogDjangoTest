from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Meet, Chank


# Create your views here.

def index(request):
    return render(request, 'mainController/index.html')


def about(request):
    return render(request, 'mainController/about.html')


def style(request):
    return render(request, 'mainController/style.html')


def promo(request):
    return render(request, 'mainController/promo.html')


# @login_required
# def calendar_view(request):
#     """Представление для календаря доступности."""
#     time_slots = TimeSlot.objects.all()
#     days = list(range(7))
#     if request.method == 'POST':
#         # Обработка формы для изменения доступности слотов
#         for day in range(7):
#             for slot in time_slots:
#                 if slot.day_of_week == day:
#                     slot_id = f"slot_{day}_{slot.id}"
#                     if slot_id in request.POST:
#                         slot.is_available = not slot.is_available
#                         slot.save()
#         return redirect('calendar')
#
#     context = {'time_slots': time_slots, 'days': days}
#     return render(request, 'mainController/calendar.html', context)


# @login_required
# def make_appointment(request):
#     """Представление для записи на прием."""
#     time_slots = TimeSlot.objects.all()
#
#     if request.method == 'POST':
#         # Обработка формы для записи
#         selected_date = request.POST.get('date')
#         selected_slot_id = request.POST.get('time_slot')
#
#         if selected_date and selected_slot_id:
#             selected_slot = TimeSlot.objects.get(pk=selected_slot_id)
#             if selected_slot.is_available:
#                 # Проверка, не назначено ли уже на этот слот
#                 if not Appointment.objects.filter(
#                     date=selected_date,
#                     time_slot=selected_slot_id
#                 ).exists():
#                     Appointment.objects.create(
#                         user=request.user,
#                         time_slot=selected_slot,
#                         date=selected_date
#                     )
#                     return redirect('appointments') # Страница с записями
#                 else:
#                     # Сообщение об ошибке: слот уже занят
#                     pass # Замените на отображение сообщения
#             else:
#                 # Сообщение об ошибке: слот недоступен
#                 pass # Замените на отображение сообщения
#         else:
#             # Сообщение об ошибке: выберите дату и время
#             pass # Замените на отображение сообщения
#
#     context = {'time_slots': time_slots}
#     return render(request, 'appointment.html', context)



def calendar(request):
    return render(request, 'mainController/calendar.html')