#Elena Savić 21/0332
#Petar Milojević 21/0336
#Ilija Miletić 21/0335
#Magdalena Obradović 21/0304

from django.shortcuts import render
from django.http import HttpResponse
from .models import *

# Create your views here.

import  os
def login(request):
    return render(request, 'EasyQuizzy/loginPage.html')

def find(request, room_name):

    return render(request, "EasyQuizzy/finding_opponent.html", {"room_name": room_name, 'korIme':request.user.username})