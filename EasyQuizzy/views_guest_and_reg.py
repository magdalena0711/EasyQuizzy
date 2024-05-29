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
    Pomoćna funkcija koja vraća korisnika na osnovu njegovog korisničkog imena
    Mora da uzme sve vrste korisnika iz baze, jer se nalaze u različitim tabelama
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
    """
    Pomoćna funkcija koja vraća rank korisnika na osnovu njegovog imena
    Koristi se u funkciji za statistiku
    :param korIme:
    :return:
    """
    users = Korisnik.objects.filter(vazeci=1).order_by('-broj_poena').all()
    i = 1
    for user in users:
        if user.korisnicko_ime == korIme:
            return i
        i +=1
    return i

def questionOfTheDay():
    """
    Pomoćna funkcija koja uzima jedno random pitanje koje će
    biti prikazano u gornjem desnom uglu kao pitanje dana
    :return:
    """
    questions = Pitanje.objects.all()
    rand = random.randint(1,len(questions)-1)
    return questions[rand].tekst_pitanja, questions[rand].tacan_odgovor, questions[rand].netacan1, questions[rand].netacan2, questions[rand].netacan3

def myContext(korIme):
    """
    Pomoćna funkcija koja vraća 'kontekst' korisnika na osnovu njegovog korisničkog imena
    Pod kontekstom se ovde
    :param korIme:
    :return:
    """
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
    role = myRole(korisnik.username)
    """
    U promenljivoj role se nalazi broj koji nam govori 
    Ulogu trenutnog korisnika
    """
    currUser = currentUser(korisnik.username)
    myRank = findMyRank(korisnik.username)
    """U promenljivoj myRank se nalazi rang korisnika"""

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
    """
    For petlja služi da u zavisnosti od korisnika i njegove uloga, u kontekst ubaci rank, korisničko ime,
    broj poena stikere za levi i desni navigacioni meni
    """
    return HttpResponse(template.render(context, request))

def loginAsGuest(request):
    """
    Funkcija za prijavu gosta, jer je loginUser funkcija loginRequired funkcija, a gost je korisnik se ne prijavljuje
    :param request:
    :return:
    """
    questions = Pitanje.objects.all().order_by('-prosecna_ocena')[:3]
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

    """
    Pomoćna funkcija koja vraća ulogu korisnika na osnovu njegovog korisničkog imena
    Samo registrovani korisnici imaju uloge, gosti nemaju
    Ako je korisnik administrator, vraćamo broj 2
    Ako je korisnik moderator, vraćamo broj 1
    Ako je korisnik samo registrovan, bez dodatnih zaduženja, vraćamo broj 0
    :param korIme:
    :return:
    """
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
    """
    Pomoćna funkcija koja proverava da li je odgovor tačan
    Ovu funkciju koristi funkcija koja je zadužena za odgovaranje na pitanje dana
    :param text:
    :param answer:
    :return:
    """
    questions = Pitanje.objects.filter(tekst_pitanja=text).first()

    if questions.tacan_odgovor == answer:
        return True
    return False

#funkcija koja je zadužena za glavnu stranicu
#dinamički učitava najbolje ocenjena pitanja
#kao i levi i desni navigacioni meni koji se razlikuju u zavisnosti od tipa korisnika
@login_required(login_url='login')
def main(request):
    """
    Funkcija za glavnu, tj. početnu stranicu
    Ona obrađuje tri najbolje ocenjena pitanja i na osnovu uloge korisnika
    kao kontekst vraća različite izglede za levi i desni meni
    """

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
    """
    Pomoćna funkcija za obradu pitanja dana
    """
    data = request.body.decode()
    print(data)

    pitanje = data.split("=")[1]
    odgovor = data.split("=")[3]

# funkcija za prijavu korisnika
# ako podaci koji su uneti u polje za korisničko ime i lozinku pronađeni u bazi,
# u sesiji će biti sačuvano korisničko ime korisnika i njegova uloga, i korisnik će
# biti prebačen na odgovarajuću početnu stranu
def loginUser(request):
    """
    Funkcija za prijavu korisnika
    U slučaju da je korisnik već prijavljen, biće odmah prebačen na glavnu stranicu
    U suprotnom će uneti podaci biti provereni, i ako se poklapaju sa podacima iz baze
    Korisnik će biti prebačen na glavnu stranicu
    """
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

    # Ako je zahtev GET ili neki drugi metod, ostaje se na istoj strani
    return HttpResponse(template.render(context, request))


#pomoćna funkcija koja proverava da li pitanje sa zadatim tekstom već postoji
#jer je tekst pitanja u bazi deinisam kao UNIQUE
def checkIfQuestionExists(text):
    """
    Pomoćna funkcija koja proverava da li pitanje već postoji u bazi
    Ovu funkciju koristi funkcija koja ubacuje pitanja u bazu prilikom predlaganja
    :param text:
    :return:
    """
    allQuestions = Pitanje.objects.all().filter(tekst_pitanja=text)

    if len(allQuestions) == 0:
        return False
    return True

#funkcija za predlaganje pitanja
@login_required(login_url='login')
def questionSuggestion(request):
    """
    Funkcija za predlaganje pitanja
    Tekst pitanja koje korisnik predloži, prvo se proveri da li već postoji u bazi
    Ako ne postoji, upisuje se sa statusom 2, što znači da je pitanje predloženo
    Ostale podatke će dodati moderator/administrator koji odobri pitanje
    """
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

    """
    Pomoćna funkcija koja proverava da li korisnik sa korisničkim imenom postoji
    Koriste je funkcije za prijavu i registraciju
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
                return True
        i+=1
    return False



# funkcija za registraciju korisnika
# sve prosledjene podatke upisuje u bazu
# u slučaju da neki od podataka nije zadovoljio određene kriterijume, biće prikazana odgovarajuća greška
def register(request):
    """
    Funkcija za registraciju korisnika
    U slučaju da je registracija uspešna, u bazi se pravi novi korisnik kome je primarna uloga registrovani korisnik
    :param request:
    :return:
    """
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
@login_required(login_url='login')
def logoutUser(request):
    """
    Funkcija za odjavu korisnika
    S obzirom da se pri prijavi, u bazi koristi i djangova tabela auth_user
    Prilikom odjave, neophodno je da se novonapravljeni red vezan za korisnika koji se odjavljuje, obriše
    :param request:
    :return:
    """
    korisnik = AuthUser.objects.get(username=request.user.username)
    korisnik.delete()

    logout(request)
    return redirect('/easyquizzy')