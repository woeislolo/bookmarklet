from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

from .models import *


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', 
                               widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', 
                               widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', 
                               widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', 
                             widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', 
                                widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', 
                                widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email уже используется.')
        return data


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=32, 
                                 label='Имя',
                                 widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=32, 
                                label='Фамилия',
                                widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(max_length=32, 
                            label='Email',
                            widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'photo']

    def clean_email(self):
        data = self.cleaned_data['email']
        qs = User.objects.exclude(id=self.instance.id)\
            .filter(email=data)
        if qs.exists():
            raise forms.ValidationError('Email уже используется.')
        return data
