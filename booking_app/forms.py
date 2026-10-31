from django import forms
from django.utils import timezone
from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'location']
        labels = {'booking_date': 'Date', 'location': 'Address'}
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data['booking_date']
        if booking_date < timezone.localdate():
            raise forms.ValidationError('The date cannot be in the past.')
        return booking_date
