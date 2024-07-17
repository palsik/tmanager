from django import forms
from urllib3.util import request

from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from apps.home.models import Profile
from django.contrib.auth.models import User


class profileForm(forms.ModelForm):
    # username = forms.CharField(
    #     label="Username", widget=forms.TextInput(attrs={'class': 'form-control mb-3',
    #                                                     'placeholder': 'Enter username on the right'}))
    # email = forms.CharField(
    #     label="Email", widget=forms.TextInput(attrs={'class': 'form-control mb-3',
    #                                                  'placeholder': 'Enter email on the right'}))
    firstName = forms.CharField(
        label="First Name", widget=forms.TextInput(attrs={'class': 'form-control mb-4', 'placeholder': 'Enter First '
                                                                                                       'Name'}))
    lastName = forms.CharField(
        label="Last Name", widget=forms.TextInput(attrs={'class': 'form-control mb-4', 'placeholder': 'Enter Last Name'}))
    address = forms.CharField(
        label="Address", widget=forms.TextInput(attrs={'class': 'form-control mb-4',
                                                       'placeholder': 'Address'}))
    aboutInfo = forms.CharField(
        label="About info", widget=forms.Textarea(attrs={'class': 'form-control mb-4',
                                                         'placeholder': 'Enter a quick bio'}))

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('firstName', css_class='form-group col-md-6'),
                Column('LastName', css_class='form-group col-md-6')),
            Row(
                Column('address', css_class='form-group col-md-6')),
            Row(
                Column('aboutInfo', css_class='form-group col-md-6')),
            Submit('submit', 'Save Changes', css_class="btn btn-primary me-2"),

        )

    class Meta:
        model = Profile
        fields = ['firstName', 'lastName', 'address', 'aboutInfo']
    # username = forms.CharField()
    # email = forms.CharField()
    # firstname = forms.CharField()
    # lastname = forms.CharField()
    # address = forms.CharField()
    # aboutinfo = forms.CharField()

    class Meta:
        model = Profile
        fields = ['username', 'email', 'firstname', 'lastname', 'address', 'aboutinfo']

    def save(self, *args, **kwargs):
        user = self.instance.User
        User.first_name = self.cleaned_data.get('firstName')
        User.last_name = self.cleaned_data.get('lastName')
        user.save()
        profile = super(profileForm, self).save(*args, **kwargs)
        return profile



