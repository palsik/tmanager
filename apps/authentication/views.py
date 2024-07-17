# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from core.settings import GITHUB_AUTH
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from apps.authentication.forms import UserRegistrationForm
from django.contrib.auth.models import User  # Import the User model
from apps.home.models import *

from django.contrib.auth.models import User
from datetime import datetime

from django.contrib.auth import authenticate, login
# from apps.authentication.models import Profile1
#from .models import Personnel, Client
from apps.home.models import *
from apps.home.views import *
from django.http import JsonResponse
from django.db.models import Max


def login_view2(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                try:
                    profile = Profile1.objects.get(user=user)
                    user_type = profile.user_type
                    department = profile.department

                    if user_type == 'supervisor':
                        # Handle supervisor login logic
                        login(request, user)
                        return redirect('supervisor_dashboard')
                    elif user_type == 'personnel' and department == 'auditing':
                        # Handle personnel with auditing department login logic
                        login(request, user)
                        return redirect('auditing_dashboard')
                    elif user_type == 'personnel' and department == 'bookkeeping':
                        # Handle personnel with bookkeeping department login logic
                        login(request, user)
                        return redirect('bookkeeping_dashboard')
                    else:
                        msg = 'Invalid user type or department'
                except Profile1.DoesNotExist:
                    # User exists but does not have a Profile1 object
                    login(request, user)
                    return render(request, "home/index3.html")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

def login_view1(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg, "GITHUB_AUTH": GITHUB_AUTH})


@csrf_protect
# Define the view function to handle form submission

def register_user1(request):
    if request.method == 'POST':
        user_type = request.POST['userType']
        username = request.POST['username']
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        department = request.POST.get('department')
        company = request.POST.get('company')

        # Create a new User instance
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create a new Profile1 instance based on user type
        if user_type == 'supervisor':
            profile = Profile1.objects.create(
                user=user,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone=phone,
                password=password
            )
            profile.save()
            return redirect('home/index3.html')

        elif user_type == 'personnel':
            profile = Profile1.objects.create(
                user=user,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone=phone,
                department=department,
                password=password
            )
            profile.save()
            initialize_task_count_for_new_personnel(user, department)
            return redirect('home/index3.html')

        elif user_type == 'client':
            profile = Profile1.objects.create(
                user=user,
                user_type=user_type,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                password=password
            )
            profile.save()
            return redirect('home/index3.html')

    return render(request, 'home/index3.html')
    if request.method == 'POST':
        user_type = request.POST['userType']
        username = request.POST['username']
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        email = request.POST['email']
        password = request.POST['password']
        phone = request.POST['phone']
        department = request.POST.get('department')
        company = request.POST.get('company')

        # Create a new User instance
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create a new Profile1 instance based on user type
        if user_type == 'supervisor':
            print('User type supervisor detected')
            profile = Profile1.objects.create(
                user=user,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone=phone,
                password=password
            )
            profile.save()
            return redirect('home/index3.html')

        elif user_type == 'personnel':
            print('User type personnel detected')
            profile = Profile1.objects.create(
                user=user,
                user_type=user_type,
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone=phone,
                department=department,
                password=password
            )
            profile.save()
            
            # Initialize task count for the new personnel
            initialize_task_count_for_new_personnel(user, department)

            return redirect('home/index3.html')

        elif user_type == 'client':
            print('User type client detected')
            profile = Profile1.objects.create(
                user=user,
                user_type=user_type,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                company=company,
                password=password
            )
            profile.save()
            return redirect('home/index3.html')

    return render(request, 'home/index3.html')




def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
