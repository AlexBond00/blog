from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.forms import ModelForm, PasswordInput, IntegerField, CharField
from django import forms


class RegistrationForm(ModelForm):
    user_name = CharField()
    password = CharField(widget=PasswordInput)


class SignupForm(UserCreationForm):
    phone_number = IntegerField(help_text="Номер телефона", required=False)
    city = CharField(max_length=30, help_text="Город проживания", required=False)

    class Meta:
        model = User
        fields = ('username', 'last_name', 'password1', 'password2', 'city', 'phone_number',)



class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('city', 'phone_number', 'verification_flag', 'superuser_flag',)


class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'last_name',)


class ContactForm(forms.Form):
    from_email = forms.EmailField(label='Email', required=True)
    subject = forms.CharField(label='Тема', required=True)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea, required=True)