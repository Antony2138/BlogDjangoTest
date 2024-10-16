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
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['background_color'].widget.attrs['value'] = self.instance.background_color

    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: First Consultation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "Example: Overview of client's needs."
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'HH:MM:SS, (example: 00:15:00 for 15 minutes)'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Example: 100.00 (0 for free)'
            }),
        }