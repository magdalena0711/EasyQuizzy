from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.

import  os
def login(request):
    return render(request, 'EasyQuizzy/loginPage.html')