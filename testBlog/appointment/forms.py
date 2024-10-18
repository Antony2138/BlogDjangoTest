from importlib.resources._common import _

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
