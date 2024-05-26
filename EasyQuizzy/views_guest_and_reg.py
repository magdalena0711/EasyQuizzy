#Magdalena Obradović 2021/0304

from datetime import datetime
import random
import docutils
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .stickers import leftAdmin, rightAdmin, leftRegistered, rightRegistered, leftModerator, rightModerator, leftGuest, rightGuest
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import *


import  os


#pomoćna funkcija koja vraća korisnika na osnovu korisničkog imena
def currentUser(korIme):
    """
    Pomocna funkcija koja vraca korisnika na osnovu njegovog korisnickog imena
    :param korIme:
    :return:
    """
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

#pomoćna funkcija koja vraća rank korisnika sa zadatim korisničkim imenom
def findMyRank(korIme):
    users = Korisnik.objects.filter(vazeci=1).order_by('-broj_poena').all()

    i = 1
    for user in users:
        if user.korisnicko_ime == korIme:
            return i
        i +=1
    return i

def questionOfTheDay():
    questions = Pitanje.objects.all()

    rand = random.randint(1,len(questions)-1)

    return questions[rand].tekst_pitanja, questions[rand].tacan_odgovor, questions[rand].netacan1, questions[rand].netacan2, questions[rand].netacan3

def myContext(korIme):
    role = myRole(korIme)

    if role == 2:
        return leftAdmin, rightAdmin
    if role == 1:
        return leftModerator, rightModerator
    if role == 0:
        return leftRegistered, rightRegistered

@login_required(login_url='login')
def statistics(request):
    """
    Funkcija koja vraća 10 najbolje rangiranih igrača
    Korisnik koji je trenutno ulogovan će sa desne strane videti svoje poene i rank
    :param request:
    :return:
    """
    users = Korisnik.objects.filter(vazeci=1)
    users = users.order_by('-broj_poena').all()

    users = users[:10]

    template = loader.get_template('EasyQuizzy/statistics.html')
    all_users = list()
    users_objects = [users]

    i = 0

    korisnik = request.user

    """
    Korisniku će se vratiti njegova uloga (registrovani korisnik - 0, moderator - 1, admin - 2)
    """
    role = myRole(korisnik.username)
    currUser = currentUser(korisnik.username)
    myRank = findMyRank(korisnik.username)
    for user in users_objects[i]:
        user_list = list()
        user_list.append(i+1)
        user_list.append(user.korisnicko_ime)
        user_list.append(user.broj_poena)
        all_users.append(user_list)
        i += 1

    if role == 0:
        context = {
            'all_users': all_users,
            'korIme': request.user.username,
            'nivo': myRank,
            'broj_poena': currUser.idkor.broj_poena,
            'left': leftRegistered,
            'right': rightRegistered
        }
    if role == 1:
        context = {
            'all_users': all_users,
            'korIme': request.user.username,
            'nivo': myRank,
            'broj_poena': currUser.idkor.broj_poena,
            'left': leftModerator,
            'right': rightModerator
        }
    if role == 2:
        context = {
            'all_users': all_users,
            'korIme': request.user.username,
            'nivo': myRank,
            'broj_poena': currUser.idkor.broj_poena,
            'left': leftAdmin,
            'right': rightAdmin
        }

    return HttpResponse(template.render(context, request))



def loginAsGuest(request):
    """
    Posebna funkcija za prijavu gosta, jer je loginUser loginRequired funkcija, a gost je korisnik se ne prijavljuje

    :param request:
    :return:
    """

    questions = Pitanje.objects.all().order_by('-prosecna_ocena')[:3]

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

    template = loader.get_template('EasyQuizzy/mainGuestPage.html')

    context = {
        'left': leftGuest,
        'right': rightGuest,
        'all_questions': bestQuestions
    }

    return HttpResponse(template.render(context, request))
# pomoćna funkcija koja vraća ulogu korisnika sa zadatim korisničkim imenom
#  0 - registrovani korisnik
#  1 - moderator
#  2 - administrator
def myRole(korIme):
    if korIme == '':
        return -1

    users = RegistrovaniKorisnik.objects.select_related('idkor')
    moder = Moderator.objects.select_related('idkor')
    admin = Administrator.objects.select_related('idkor')

    for user in users:
        if user.idkor.korisnicko_ime == korIme:
            return 0

    for user in moder:
        if user.idkor.korisnicko_ime == korIme:
            return 1

    for user in admin:
        if user.idkor.korisnicko_ime == korIme:
            return 2


def checkIfAnswerIsCorreect(text, answer):
    questions = Pitanje.objects.filter(tekst_pitanja=text).first()

    if questions.tacan_odgovor == answer:
        return True
    return False

#funkcija koja je zadužena za glavnu stranicu
#dinamički učitava najbolje ocenjena pitanja
#kao i levi i desni navigacioni meni koji se razlikuju u zavisnosti od tipa korisnika
@login_required(login_url='login')
def main(request):
    context={}

    korisnik = request.user
    role = myRole(korisnik.username)

    questions = Pitanje.objects.all().order_by('-prosecna_ocena')[:3]

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
    tekst_pitanja, tacan, netacan1, netacan2, netacan3 = questionOfTheDay()
    if role == 0:
        context = {
            'tekst_pitanja': tekst_pitanja,
            'tacan_odgovor': tacan,
            'netacan1': netacan1,
            'netacan2': netacan2,
            'netacan3': netacan3,
            'all_questions': bestQuestions,
            'left': leftRegistered,
            'right': rightRegistered

        }
    if role == 1:
        context = {
            'tekst_pitanja': tekst_pitanja,
            'tacan_odgovor': tacan,
            'netacan1': netacan1,
            'netacan2': netacan2,
            'netacan3': netacan3,
            'all_questions': bestQuestions,
            'left': leftModerator,
            'right': rightModerator
        }
    if role == 2:
        context = {
            'tekst_pitanja': tekst_pitanja,
            'tacan_odgovor': tacan,
            'netacan1': netacan1,
            'netacan2': netacan2,
            'netacan3': netacan3,
            'all_questions': bestQuestions,
            'left': leftAdmin,
            'right': rightAdmin
        }


    return HttpResponse(template.render(context, request))

def dayQuestion(request):
    data = request.body.decode()
    print(data)

    pitanje = data.split("=")[1]
    odgovor = data.split("=")[3]




# funkcija za prijavu korisnika
# ako podaci koji su uneti u polje za korisničko ime i lozinku pronađeni u bazi,
# u sesiji će biti sačuvano korisničko ime korisnika i njegova uloga, i korisnik će
# biti prebačen na odgovarajuću početnu stranu
def loginUser(request):
    template = loader.get_template('EasyQuizzy/loginPage.html')

    context = {}
    if request.user.is_authenticated:
        return redirect('main')

    if request.method == 'POST':
        korIme = request.POST.get('username')
        password = request.POST.get('password')
        registeredUsers = RegistrovaniKorisnik.objects.select_related('idkor')
        moderatorUsers = Moderator.objects.select_related('idkor')
        adminUsers = Administrator.objects.select_related('idkor')

        if request.user.is_authenticated:
            return redirect('main')

        for user in registeredUsers:

            if user.idkor.korisnicko_ime == korIme and user.idkor.lozinka == password and user.idkor.vazeci == 1:
                # Ako je korisnik pronađen, prelazi na sledeću stranicu
                context = {
                    'korisniko_ime': korIme,
                }

                msg = "Login Successful"
                request.session['korIme'] = korIme
                request.session['IdKor_current'] = user.idkor.idkor
                request.session['role'] = 'registrovani'
                # AuthUser.objects.create(
                #     username=korIme,
                #     password=password,
                #     email=user.idkor.email,
                #     first_name=user.idkor.ime,
                #     last_name=user.idkor.prezime,
                #     is_active=True,
                #     is_staff=True,
                #     is_superuser=False,
                #     date_joined=datetime.now()
                # )
                userRet = User.objects.create_user(username=korIme, password=password)
                login(request, userRet)
                return redirect('main')

        for user in moderatorUsers:

            if user.idkor.korisnicko_ime == korIme and user.idkor.lozinka == password and user.idkor.vazeci == 1:
                # Ako je korisnik pronađen, prelazi na sledeću stranicu
                context['korisnicko_ime']= korIme

                msg = "Login Successful"
                request.session['korIme'] = korIme
                request.session['IdKor_current'] = user.idkor.idkor
                request.session['role'] = 'moderator'
                userRet = User.objects.create_user(username=korIme, password=password)
                login(request, userRet)
                return redirect('main')

        for user in adminUsers:
            if user.idkor.korisnicko_ime == korIme and user.idkor.lozinka == password and user.idkor.vazeci == 1:
                # Ako je korisnik pronađen, prelazi na sledeću stranicu
                context = {
                    'korisniko_ime': korIme,
                }
                msg = "Login Successful"
                request.session['korIme'] = korIme
                request.session['IdKor_current'] = user.idkor.idkor
                request.session['role'] = 'admin'
                userRet = User.objects.create_user(username=korIme, password=password)
                login(request, userRet)
                return redirect('main')

        # Ako korisnik nije pronađen, ispisuje se greška
        messages.error(request, 'Pogrešno korisničko ime ili lozinka.')
        msg = "Uneli ste pogrešno ime ili lozinku."
        context['message'] = msg
        return HttpResponse(template.render(context, request))



    # Ako je zahtev GET ili neki drugi metod, jednostavno prikaži stranicu za prijavu
    return HttpResponse(template.render(context, request))


#pomoćna funkcija koja proverava da li pitanje sa zadatim tekstom već postoji
#jer je tekst pitanja u bazi deinisam kao UNIQUE
def checkIfQuestionExists(text):
    allQuestions = Pitanje.objects.all().filter(tekst_pitanja=text)

    if len(allQuestions) == 0:
        return False
    return True

#funkcija za predlaganje pitanja
@login_required(login_url='login')
def questionSuggestion(request):
    template = loader.get_template('EasyQuizzy/question_suggestions.html')
    context ={}

    korisnik = request.user
    role = myRole(korisnik.username)

    if role == 0:
        context = {
            'korIme': korisnik.username,
            'left': leftRegistered,
            'right': rightRegistered
        }
    if role == 1:
        context = {
            'korIme': korisnik.username,
            'left': leftModerator,
            'right': rightModerator
        }
    if role == 2:
        context = {
            'korIme': korisnik.username,
            'left': leftAdmin,
            'right': rightAdmin
        }

    if request.method == 'POST':
        text = request.POST.get('text')

        if checkIfQuestionExists(text) == True:
            context['text'] = "Pitanje sa zadatim tekstom već postoji!"



        else:
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


#pomoćna funkcija koja proverava da li korisnik sa zadatim imenom već postoji
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



# funkcija za registraciju korisnika
# sve prosledjene podatke upisuje u bazu
# u slučaju da neki od podataka nije zadovoljio određene kriterijume, biće prikazana odgovarajuća greška
def register(request):

    template = loader.get_template('EasyQuizzy/registration.html')
    context = {}
    if request.method == 'POST':
        korIme = request.POST.get('username')

        exists = checkIfUserExists(korIme)
        if(exists):
            context['message'] = 'Korisničko ime je zauzeto!'
            return HttpResponse(template.render(context, request))

        
        ime = request.POST.get('name')
        prezime = request.POST.get('surname')
        password = request.POST.get('password')
        pass_check = request.POST.get('passwordVal')

        if( password != pass_check):
            context['message'] = 'Lozinke se ne poklapaju!'
            return HttpResponse(template.render(context, request))
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
        context['message'] = 'Uspešno ste se registrovali!'

        return redirect('register')

    return HttpResponse(template.render(context, request))

# funkcija za odjavljivanje korisnika
# briše korisnika iz Djangove tabele AuthUser
def logoutUser(request):
    # template = loader.get_template('EasyQuizzy/regMainPage.html')
    # context = {}
    #
    # if request.method == 'GET':
    #     korIme= request.session.get('korIme')
    #
    #     korisnik = AuthUser.objects.get(username=korIme)
    #     korisnik.delete()
    #
    #     request.session['korIme'] = ''
    #     request.session['role'] = ''
    #
    #     return redirect('login')
    #
    # return HttpResponse(template.render(context, request))
    korisnik = AuthUser.objects.get(username=request.user.username)
    korisnik.delete()

    logout(request)
    return redirect('/easyquizzy')