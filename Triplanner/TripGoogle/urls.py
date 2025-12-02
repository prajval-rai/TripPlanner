# users/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('google_place_search/', google_place_search, name="register-user")
]
