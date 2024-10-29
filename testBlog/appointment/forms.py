from django import forms
from django.contrib.auth.models import User

from .models import (
    Appointment, AppointmentRequest, Service, StaffMember, WorkingHours, DayOff
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


class PersonalInformationForm(forms.Form):
    # first_name, last_name, email
    first_name = forms.CharField(max_length=50, label='Имя:', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=50, label='Фамилия', widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # pop the user from the kwargs
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user:
            if self.user.email == email:
                return email
            queryset = User.objects.exclude(pk=self.user.pk)
        else:
            queryset = User.objects.all()

        if queryset.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email


class StaffAppointmentInformationForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['services_offered', 'slot_duration', 'lead_time', 'finish_time',
                  'appointment_buffer_time']
        labels = {
            'services_offered': 'Выберите услуги для работника:',
            'slot_duration': 'Частота записи в минутах:',
            'lead_time': 'Время начала работы:',
            'finish_time': 'Время окончания работы:',
            'appointment_buffer_time': 'Через сколько будет разрешена запись с начала рабочего времени:',
        }
        widgets = {
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


class StaffDaysOffForm(forms.ModelForm):
    class Meta:
        model = DayOff
        fields = ['start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'datepicker',
                'placeholder': 'Начало выходных'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'datepicker',
                'placeholder': 'Начало выходных'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Причина выходного дня'
            }),

        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class StaffWorkingHoursForm(forms.ModelForm):
    class Meta:
        model = WorkingHours
        fields = ['day_of_week', 'start_time', 'end_time']
