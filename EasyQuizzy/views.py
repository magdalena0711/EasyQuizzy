from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.

import  os
def login(request):
    all_objects = Kategorija.objects.all()
    str = ''
    print(os.environ["PASSWORD"])
    for obj in all_objects:
        str += obj
    return HttpResponse(str)