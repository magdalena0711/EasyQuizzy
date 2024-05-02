from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import *

# Create your views here.

import  os

'''funkcija za dohvatanje 10 najboljih igraca
u slučaju da trenutno ulogovan igrač nije među najbolje rangiranih 10
njegov rang se prikazuje odvojeno'''
def statistics(request):
    users = RegistrovaniKorisnik.objects.select_related('idkor')

    template = loader.get_template('EasyQuizzy/statistics.html')
    topTen = list()
    users_objects = [users]

    i = 0

    for user in users_objects[i]:
        user_list = list()
        user_list.append(i+1)
        user_list.append(user.idkor.korisnicko_ime)
        user_list.append(user.idkor.broj_poena)
        topTen.append(user_list)
        i += 1
    topTen.sort(key=lambda x: x[2])
    #all_users.sort(key=user.idkor.broj_poena)
    context = {
        'all_users': topTen
    }
    return HttpResponse(template.render(context, request))