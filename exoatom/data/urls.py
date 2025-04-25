# myapp/urls.py
from django.urls import path
from data.views import exoatom_search

urlpatterns = [
    path('search/', exoatom_search, name='exoatom_search'),
]
