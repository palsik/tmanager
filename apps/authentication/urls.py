# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, include
from .views import login_view2, register_user
from django.contrib.auth.views import LogoutView
from apps.authentication.views import *

#To support media
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin





urlpatterns = [
    path('login/', login_view2, name="login"),
    path('register1/', register_user1, name="register1"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('social_login/', include('allauth.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
