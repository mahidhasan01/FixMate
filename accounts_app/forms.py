from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from .models import CustomerProfile, User, WorkerProfile


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class CustomerSignUpForm(SignUpForm):
    address = forms.CharField(max_length=255, required=False)

    field_order = ['username', 'first_name', 'last_name', 'email', 'phone', 'address']

    def save(self):
        with transaction.atomic():
            user = super().save(commit=False)
            user.role = User.CUSTOMER
            user.save()
            CustomerProfile.objects.create(user=user, address=self.cleaned_data['address'])
        return user


class WorkerSignUpForm(SignUpForm):
    skill = forms.CharField(max_length=100)
    experience = forms.IntegerField(min_value=0, max_value=60, initial=0,
                                    label='Experience (years)')

    field_order = ['username', 'first_name', 'last_name', 'email', 'phone', 'skill', 'experience']

    def save(self):
        with transaction.atomic():
            user = super().save(commit=False)
            user.role = User.WORKER
            user.save()
            WorkerProfile.objects.create(
                user=user,
                skill=self.cleaned_data['skill'],
                experience=self.cleaned_data['experience'],
            )
        return user
