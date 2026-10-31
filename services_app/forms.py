from django import forms

from .models import ServiceListing


class ServiceListingForm(forms.ModelForm):
    class Meta:
        model = ServiceListing
        fields = ['category', 'title', 'description', 'price', 'service_image']
        labels = {'price': 'Price (৳)', 'service_image': 'Photo'}
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'service_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
