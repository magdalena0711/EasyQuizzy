from django.contrib import admin
from django.urls import path, include
from EasyQuizzy import views

urlpatterns = [
    path('', views.statistics, name='statistics')
]