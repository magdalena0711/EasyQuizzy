from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import *

# Create your views here.

import  os

def currentUser(korIme):
    users = RegistrovaniKorisnik.objects.select_related('idkor')
    moder = Moderator.objects.select_related('idkor')
    admin = Administrator.objects.select_related('idkor')

    types = ['admin', 'moderator', 'korisnik']
    users_objects = [admin, moder, users]

    i = 0
    for tp in types:
        for user in users_objects[i]:
            if user.idkor.korisnicko_ime == korIme:
                return user
        i += 1
    return users[0]

def findMyRank(korIme):
    users = RegistrovaniKorisnik.objects.select_related('idkor').order_by('-idkor__broj_poena')

    i = 0
    for user in users:
        if user.idkor.korisnicko_ime == korIme:
            return i
        i +=1
    return i

def statistics(request):
    users = RegistrovaniKorisnik.objects.select_related('idkor').order_by('-idkor__broj_poena')
    users = users.filter(idkor__vazeci=1)
    user = users[:10]

    template = loader.get_template('EasyQuizzy/statistics.html')
    all_users = list()
    users_objects = [users]

    i = 0
    for user in users_objects[i]:
        user_list = list()
        user_list.append(i+1)
        user_list.append(user.idkor.korisnicko_ime)
        user_list.append(user.idkor.broj_poena)
        all_users.append(user_list)
        i += 1

    context = {
        'all_users': all_users
    }

    currUser = currentUser(request.session['korIme'])
    myRank = findMyRank(request.session['korIme'])
    context = {
        'all_users': all_users,
        'korIme': currUser.idkor.korisnicko_ime,
        'nivo': myRank+1,
        'broj_poena': currUser.idkor.broj_poena
    }


    return HttpResponse(template.render(context, request))

def main(request):
    questions = Pitanje.objects.all().order_by(''
                                               'prosecna_ocena')[:3]
    template = loader.get_template('EasyQuizzy/regMainPage.html')
    bestQuestions = list()
    quest_objects = [questions]

    i = 0
    for quest in quest_objects[i]:
        quest_list = list()
        quest_list.append(i + 1)
        quest_list.append(quest.tekst_pitanja)
        quest_list.append(quest.tacan_odgovor)
        quest_list.append(quest.prosecna_ocena)
        bestQuestions.append(quest_list)
        i += 1

    context = {
        'all_questions': bestQuestions
    }
    return HttpResponse(template.render(context, request))

'''funkcija za prijavu korisnika
ako podaci koji su uneti u polje za korisničko ime i lozinku pronađeni u bazi,
u sesiji će biti sačuvano korisničko ime korisnika i njegova uloga, i korisnik će
biti prebačen na odgovarajuću početnu stranu'''
def login(request):
    template = loader.get_template('EasyQuizzy/loginPage.html')

    context = {}

    if request.method == 'POST':
        korIme = request.POST.get('username')
        password = request.POST.get('password')
        registeredUsers = RegistrovaniKorisnik.objects.select_related('idkor')
        moderatorUsers = Moderator.objects.select_related('idkor')
        adminUsers = Administrator.objects.select_related('idkor')

        for user in registeredUsers:

            if user.idkor.korisnicko_ime == korIme and user.idkor.lozinka == password:
                # Ako je korisnik pronađen, prelazi na sledeću stranicu
                context = {
                    'all_users': [],
                }

                msg = "Login Successful"
                request.session['korIme'] = korIme
                request.session['IdKor_current'] = user.idkor.idkor
                request.session['role'] = 'registrovani'
                return redirect('main')

        for user in moderatorUsers:

            if user.idkor.korisnicko_ime == korIme and user.idkor.lozinka == password:
                # Ako je korisnik pronađen, prelazi na sledeću stranicu
                context = {
                    'all_users': [],
                }

                msg = "Login Successful"
                request.session['korIme'] = korIme
                request.session['IdKor_current'] = user.idkor.idkor
                request.session['role'] = 'moderator'

                return redirect('main')

        for user in adminUsers:
            if user.idkor.korisnicko_ime == korIme and user.idkor.lozinka == password:
                # Ako je korisnik pronađen, prelazi na sledeću stranicu
                context = {
                    'all_users': [],
                }
                msg = "Login Successful"
                request.session['korIme'] = korIme
                request.session['IdKor_current'] = user.idkor.idkor
                request.session['role'] = 'admin'
                return redirect('main')

        # Ako korisnik nije pronađen, ispisuje se greška
        messages.error(request, 'Pogrešno korisničko ime ili lozinka.')
        msg = "Uneli ste pogrešno ime ili lozinku."
        context['message'] = msg
        return HttpResponse(template.render(context, request))



    # Ako je zahtjev GET ili neki drugi metod, jednostavno prikaži stranicu za prijavu
    return HttpResponse(template.render(context, request))

'''
def main(request):
    template = loader.get_template('EasyQuizzy/regMainPage.html')
    return render(request, 'EasyQuizzy/regMainPage.html')
'''
def questionSuggestion(request):
    template = loader.get_template('EasyQuizzy/question_suggestions.html')
    context ={}


    if request.method == 'POST':
        text = request.POST.get('text')

        new_question = Pitanje()
        new_question.idkat = Kategorija.objects.all().first()  # Možete koristiti .first() umjesto [0]
        new_question.tekst_pitanja = text
        new_question.tezina_pitanja = 0
        new_question.tacan_odgovor = ""
        new_question.netacan1 = ""
        new_question.netacan2 = ""
        new_question.netacan3 = ""
        new_question.status = 2
        new_question.zbir_ocena = 0
        new_question.prosecna_ocena = 0
        new_question.broj_ocena = 0
        new_question.save()


        return redirect('questionSuggestion')

    return HttpResponse(template.render(context, request))



def checkIfUserExists(korIme):
    users = RegistrovaniKorisnik.objects.select_related('idkor')
    moder = Moderator.objects.select_related('idkor')
    admin = Administrator.objects.select_related('idkor')


    types = ['admin', 'moderator', 'korisnik']
    users_objects = [admin, moder, users]

    i = 0
    for tp in types:
        for user in users_objects[i]:
            if user.idkor.korisnicko_ime == korIme:
                return True
        i+=1
    return False

'''funkcija za registraciju korisnika
sve prosledjene podatke upisuje u bazu
u slučaju da neki od podataka nije zadovoljio određene kriterijume, biće prikazana odgovarajuća greška'''
def register(request):
    template = loader.get_template('EasyQuizzy/registration.html')
    context = {}
    if request.method == 'POST':
        korIme = request.POST.get('username')

        exists = checkIfUserExists(korIme)
        if(exists):
            context['message'] = 'Korisničko ime je zauzeto!'
            return redirect('register')

        ime = request.POST.get('name')
        prezime = request.POST.get('surname')
        password = request.POST.get('password')
        email = request.POST.get('email')
        pol = request.POST.get('gender')


        newUser = Korisnik()
        newUser.korisnicko_ime = korIme
        newUser.ime = ime
        newUser.prezime = prezime
        newUser.lozinka = password
        newUser.email = email
        if pol == "Muško":
            newUser.pol = 'M'
        else:
            newUser.pol = 'Z'
        newUser.broj_poena = 0
        newUser.nivo = 1
        newUser.vazeci = 1
        newUser.save()

        RegistrovaniKorisnik.objects.create(idkor=newUser)
        context['message'] = 'Korisničko ime je zauzeto!'

        return redirect('register')

    return HttpResponse(template.render(context, request))

'''funkcija za odjavljivanje korisnika
korisničko ime i ulogu trenutno ulogovanog korisnika, briše iz sesije'''
def logout(request):
    template = loader.get_template('EasyQuizzy/regMainPage.html')
    context = {}

    if request.method == 'GET':
        request.session['korIme'] = ''
        request.session['role'] = ''
        return redirect('login')

    return HttpResponse(template.render(context, request))