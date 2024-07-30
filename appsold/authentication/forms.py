# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from apps.home.models import *


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))

# Define a custom SignUpForm based on the UserCreationForm
class UserRegistrationForm(forms.Form):
    user_type = forms.ChoiceField(choices=[('supervisor', 'Supervisor'), ('personnel', 'Personnel'), ('client', 'Client')])
    username = forms.CharField(max_length=100, required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    phone = forms.CharField(max_length=20, required=True)
    department = forms.ChoiceField(choices=[('', 'Select Department'), ('auditing', 'Auditing'), ('bookkeeping', 'Bookkeeping')], required=False)
    company = forms.CharField(max_length=100, required=False)

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')

        if user_type == 'personnel':
            phone = cleaned_data.get('phone')
            department = cleaned_data.get('department')
            if not phone:
                self.add_error('phone', 'Phone number is required for personnel.')
            if not department:
                self.add_error('department', 'Department selection is required for personnel.')

        elif user_type == 'client':
            company = cleaned_data.get('company')
            if not company:
                self.add_error('company', 'Company name is required for clients.')

        return cleaned_data


class SignUpForm(UserCreationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    

