from django import forms

from .models import (
    Appointment, AppointmentRequest, Service, StaffMember, WorkingHours
)

from .utils.validators import not_in_the_past


class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ('date', 'start_time', 'end_time', 'service', 'staff_member')


class SlotForm(forms.Form):
    selected_date = forms.DateField(validators=[not_in_the_past])
    staff_member = forms.ModelChoiceField(StaffMember.objects.all(),
                                          error_messages={'invalid_choice': 'Staff member does not exist'})


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('phone',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update(
            {
                'placeholder': '1234567890'
            })
        self.fields['additional_info'].widget.attrs.update(
            {
                'rows': 2,
                'class': 'form-control',
            })
        self.fields['address'].widget.attrs.update(
            {
                'rows': 2,
                'class': 'form-control',
                'placeholder': '1234 Main St, City, State, Zip Code',
                'required': 'true'
            })
        self.fields['additional_info'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'I would like to be contacted by phone.'
            })


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price']
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'duration': 'Продолжительность',
            'price': 'Цена',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'label': 'Название',
                'class': 'form-control',
                'placeholder': 'Пример: Наращивание'
            }),
            'description': forms.Textarea(attrs={
                'label': 'Название',
                'class': 'form-control',
                'placeholder': "Пример: Описание для клиентов."
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ЧЧ:MM:СС, (Пример: 00:15:00 для 15 минут)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример: 100.00 (0 for free)'
            }),
        }


class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['user', 'services_offered', 'slot_duration', 'lead_time', 'finish_time',
                  'appointment_buffer_time']
        labels = {
            'user': 'Выберите пользователя:',
            'services_offered': 'Выберите услуги для работника:',
            'slot_duration': 'Частота записи в минутах:',
            'lead_time': 'Время начала работы:',
            'finish_time': 'Время окончания работы:',
            'appointment_buffer_time': 'Через сколько будет разрешена запись с начала рабочего времени:',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'service_offered': forms.Select(attrs={'class': 'form-control'}),
            'slot_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример значений: 30, 60, 90, 120... (в минутах)'
            }),
            'lead_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример значений: 08:00:00, 09:00:00... (24-часовой формат)'
            }),
            'finish_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример значений: 17:00:00, 18:00:00... (24-часовой формат)'
            }),
            'appointment_buffer_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Пример значений: 15, 30, 45, 60... (в минутах)'
            })
        }
