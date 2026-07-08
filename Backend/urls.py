from django.urls import path

from Backend.views import home

urlpatterns = [
    path('',home,name='home'),
]