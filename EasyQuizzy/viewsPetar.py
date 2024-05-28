#Petar Milojević 2021/0336
import json

from django.shortcuts import render, redirect
from .models import *
import base64
import random
import math
from django.forms.models import model_to_dict
from .views_guest_and_reg import *

category=""
number_questions_chosen=0 #Sluzi kao brojac koliko smo ukupno pitanja izabrali
role_user= ""
type_game= ""
number_current_question=0 #Sluzi kao brojac do kog smo pitanja trenutno dosli
questions_test_current=[]
current_question= "" #Sluzi da bi se znalo koje je trenutno pitanje na koje se odgovara

level_current_user=1

IdKor_current=2

replacement_question= ""

replacement_question_used=False
half_half_used=False


number_won_points=0

from decimal import Decimal

#Koristi se za predstavljanje decimal u float kako bi mogao objekat da se sacuva kao JSON
def decimal_to_float(object):
    if isinstance(object, Decimal):
        return float(object)
    raise TypeError("Objekat nije DECIMAL")


#OBAVEZNO DODATI request.session['IdKor_trenutni']=IdKor_trenutni KADA SE LOGUJE KORISNIK


def home(request):

    return render(request, 'EasyQuizzy/loginPage.html')


#def proba(request):
    #OVO SAM JA STAVIO SAMO KAKO BIH MOGAO DA TESTIRAM DA LI SVE RADIIII

    #print(request.session)

    #return render(request, 'EasyQuizzy/mainGuestPage.html')

#Dugme za izradu testa
def doing_test_button(request):

    return render(request, 'EasyQuizzy/picking_choice_singleplayer_or_multiplayer.html')

#Funkcija koja radi kada se izabere tip igre i predje na stranicu za izbor kategorije i broja pitanja,tako da mora se izvuku slike svih kategorija koje postoje!
def choice_single_multi(request):
    categories=Kategorija.objects.all()
    images=[]

    role_temp = myRole(request.user.username)
    if role_temp == 0:
        request.session['role_user'] = 'registered'
    elif role_temp == 1:
        request.session['role_user'] = 'moder'
    else:
        request.session['role_user'] = 'admin'    
    


    for cat in categories:

        images.append(base64.b64encode(cat.slika).decode())



    length_range = math.ceil((len(categories)-4)/5)

    list_images=[]

    for cat in categories:
        list_images.append((cat.idkat//5)-1)

    data = list(zip(categories,images,list_images))

    if request.method == 'POST':
        choice_button = request.POST.get('test')
        if choice_button=="small_single":

            type_game="single"
            request.session['type_game']=type_game

            return render(request, 'EasyQuizzy/picking_category_number_of_questions_singleplayer.html',{'data':data,'range':range(length_range)})
        else:

            #Stavljeno samo da postoji dok se ne implenetira MULTIPLAYER
            type_game = "multi"
            request.session['type_game'] = type_game
            return render(request, 'EasyQuizzy/mainGuestPage.html',{'data':data,'range':range(length_range)})


#Funkcija koja radi kada se izabere tip igre i predje na stranicu za izbor kategorije i broja pitanja,tako da mora se izvuku slike svih kategorija koje postoje,samo za gosta!
def choice_single_multi_guest(request):
    categories=Kategorija.objects.all()
    images=[]
    request.session['type_game'] = "single"
    request.session['role_user']="guest"
    request.session['role'] = "guest"
    choice_button="small_single"

    for cat in categories:

        images.append(base64.b64encode(cat.slika).decode())



    length_range = math.ceil((len(categories)-4)/5)

    list_images=[]

    for cat in categories:
        list_images.append((cat.idkat//5)-1)

    data = list(zip(categories,images,list_images))

    if choice_button=="small_single":

        type_game="single"
        request.session['type_game']=type_game

        return render(request, 'EasyQuizzy/picking_category_number_of_questions_singleplayer.html',{'data':data,'range':range(length_range)})
    else:

        #Stavljeno samo da postoji dok se ne implenetira MULTIPLAYER
        type_game = "multi"
        request.session['type_game'] = type_game
        return render(request, 'EasyQuizzy/mainGuestPage.html',{'data':data,'range':range(length_range)})


#Funkcija koja radi kaka se izabere kategorija i broj pitanja.
#Ova funkcija vadi izabrani broj pitanja,kategoriju,pocetno pitanje, zamensko pitanje, kao i sva ostala pitanja u zavisnosti od nivoa korisnika
def choice_category_question_number(request):

    #Test

    #request.session['role_user']="K"
    #request.session['IdKor_current']=1

    if (request.session['role_user']=="guest"):
        request.session['korIme']="Gost"

    questions_all_possible_difficulties=[]
    questions_all_possible_difficulty1=[]
    questions_all_possible_difficulty2=[]
    questions_all_possible_difficulty3=[]



    questions_pulledout_difficulty1=[]
    questions_pulledout_difficulty2=[]
    questions_pulledout_difficulty3=[]


    #Test
    request.session['number_won_points'] = 0

    replacement_question_used=False
    request.session['replacement_question_used']=replacement_question_used

    half_half_used=False
    request.session['half_half_used']=half_half_used



    #IdKor_current= request.session['IdKor_current']


    questions_test_current=[]

    level_current_user=Korisnik.objects.get(idkor=IdKor_current).nivo

    if request.method == 'POST':
        #Imena html objekata mogu da budu i na srpskom,jer ih svako za sebe koristi,jer skoro svi rade na htmlovima koje su sami pravili!
        number_questions_chosen = request.POST.get('broj_pitanja')
        number_questions_chosen=int(number_questions_chosen)

        request.session['number_questions_chosen']=number_questions_chosen

        choice_button_category = request.POST.get('dugmad')

        if (choice_button_category=="opsta"):

            questions_all_possible_difficulty1 = list(Pitanje.objects.filter(tezina_pitanja=1))
            questions_all_possible_difficulty2 = list(Pitanje.objects.filter(tezina_pitanja=2))
            questions_all_possible_difficulty3 = list(Pitanje.objects.filter(tezina_pitanja=3))

        else:

            questions_all_possible_difficulties = Pitanje.objects.filter(idkat__naziv=choice_button_category)

            for p in questions_all_possible_difficulties:
                if p.tezina_pitanja==1:
                    questions_all_possible_difficulty1.append(p)
                elif p.tezina_pitanja==2:
                    questions_all_possible_difficulty2.append(p)
                else:
                    questions_all_possible_difficulty3.append(p)


    #Mozda doraditi VIDECEMO
    if level_current_user<=5:
        questions_pulledout_difficulty1=random.sample(questions_all_possible_difficulty1, number_questions_chosen+1)

    elif level_current_user<=10:
        number_difficulty1 = (number_questions_chosen+1)//2
        number_difficulty2 = (number_questions_chosen+1)-number_difficulty1

        questions_pulledout_difficulty1=random.sample(questions_all_possible_difficulty1,number_difficulty1)
        questions_pulledout_difficulty2 = random.sample(questions_all_possible_difficulty2, number_difficulty2)

    else:
        number_difficulty2 = (number_questions_chosen+1)//2
        number_difficulty3 = (number_questions_chosen+1)-number_difficulty2

        questions_pulledout_difficulty2=random.sample(questions_all_possible_difficulty2, number_difficulty2)
        questions_pulledout_difficulty3 = random.sample(questions_all_possible_difficulty3, number_difficulty3)

    for p in questions_pulledout_difficulty1:
        questions_test_current.append(model_to_dict(p))

    for p in questions_pulledout_difficulty2:
        questions_test_current.append(model_to_dict(p))

    for p in questions_pulledout_difficulty3:
        questions_test_current.append(model_to_dict(p))

    replacement_question=questions_test_current.pop(0)


    #MORA SVAKO PITANJE DA SE PRETVORI U DICTIONARY I ONDA NA SVE TO JSON.DUMPS(RECNIK)

    #print(replacement_question)



    request.session['replacement_question'] = json.dumps(replacement_question,default=decimal_to_float)

    current_question = questions_test_current.pop(0)




    #dictionary_model = model_to_dict(current_question)

    request.session['current_question'] = json.dumps(current_question,default=decimal_to_float)



    #print(questions_test_current)

    request.session['questions_test_current'] = json.dumps(questions_test_current,default=decimal_to_float)


    #Ovo su odgovori na pitanje izmesani nasumicno

    correct_incorrect_layout_answers=[current_question['tacan_odgovor'],current_question['netacan1'],current_question['netacan2'],current_question['netacan3']]
    random.shuffle(correct_incorrect_layout_answers)


    request.session['correct_incorrect_layout_answers'] = correct_incorrect_layout_answers


    #Ovi indikatori stoje kako bi znao koji je odgovor tacan a koji netacan
    correct_incorrect_layout_indicators=[]



    for ans in correct_incorrect_layout_answers:
        if ans==current_question['tacan_odgovor']:
            correct_incorrect_layout_indicators.append(1)
        else:
            correct_incorrect_layout_indicators.append(0)


    #Ovo se koristi kako bi znao da li da stavis pitanje u prvi <tr> ili u drugi <tr> kako bi imao lepo rasporedjeno 2 dugmeta po redu,kao u prototipu
    # 0 i 1 idu u prvi <tr> 2 i 3 idu u drugi <tr>

    correct_incorrect_rows_table=[0,1,2,3]

    #Ovo je sve zipovano,sto znaci da posto imamo 3 liste i sve 3 imaju isti broj elementa (po 4) sada zapravo imas 4 tupla sa po 3 clana
    # jedan tuple od 4 izgleda ovako (tekst_pitanja,indikator_tacnosti,redni_broj_koristi_se_za_<tr>)
    #Lista je napravljena kako bi mogao vise puta da iteriras kroz listu u html-u,da je bez list() mogao bi samo jednom da prodjes kroz listu
    #ovako ces moci 2 puta taman prodjes jednom za svaki row tabele (<tr>)!

    correct_incorrect_data= list(zip(correct_incorrect_layout_answers,correct_incorrect_layout_indicators,correct_incorrect_rows_table))
    request.session['correct_incorrect_data'] = json.dumps(correct_incorrect_data,default=decimal_to_float)

    #Test
    number_current_question=1



    type_game=request.session['type_game']

    request.session['number_current_question']=number_current_question




    if type_game=="single":

        #samo za probu

       # return render(request, 'EasyQuizzy/question_grading.html', {'question_text_content':current_question['tekst_pitanja'],
                                               # 'correct_incorrect_data':correct_incorrect_data})


        return redirect('choice_category_question_number_singleplayer_GET')


    else:
        #POSLE AKO STIGNEMO
        return render(request, 'EasyQuizzy/test_multiplayer.html',
                      {'korIme': request.session['korIme'],
                       'number_current_question': request.session['number_current_question'],
                       'question_text_content': current_question['tekst_pitanja'],
                       'correct_incorrect_data': correct_incorrect_data,
                       'half_half_used': request.session['half_half_used'],
                       'replacement_question_used': request.session['replacement_question_used'],
                       'disabled': [4, 4]})

#Koristi se samo kako bi moglo da se spreci da se desi nesto sto ne bi trebalo kada se uradi RELOAD stranice
def choice_category_question_number_singleplayer_GET(request):


    current_question = json.loads(request.session['current_question'])
    correct_incorrect_data = json.loads(request.session['correct_incorrect_data'])

    return render(request, 'EasyQuizzy/test_singleplayer.html',
                  {'korIme': request.session['korIme'],
                   'number_current_question': request.session['number_current_question'],
                   'question_text_content': current_question['tekst_pitanja'],
                   'correct_incorrect_data': correct_incorrect_data,
                   'half_half_used': request.session['half_half_used'],
                   'replacement_question_used': request.session['replacement_question_used'],
                   'disabled': [4, 4]})

#Koristi se kada korisnik na kraju testa izabere sta zeli da uradi, da li zeli da ode na pocetni meni ili da radi test ponovo, samo pre toga da izabere kategoriju i broj pitanja!
def test_end(request):
    if 'test ponovo' in request.POST:
        # Kod koji se izvršava ako je kliknuta dugme da se radi test ponovo

        # Ovde sam stavio da ga vrati da moze ponovo da bira kategoriju i broj pitanja,
        # jer je za sada tako lakse, da ne mora novi kod da se pise za ponovo vadjenje novih pitanja, koja nisu do sada bila itd,
        # jer bi ovako mogao da se desi slucaj da igrac dobije bas veliki broj ponovoljenih pitanja

        categories = Kategorija.objects.all()
        images = []

        for cat in categories:
            images.append(base64.b64encode(cat.slika).decode())

        length_range = math.ceil((len(categories) - 4) / 5)

        list_images = []

        for cat in categories:
            list_images.append((cat.idkat // 5) - 1)

        data = list(zip(categories, images, list_images))

        return render(request, 'EasyQuizzy/picking_choice_singleplayer_or_multiplayer.html',{'data':data,'range':range(length_range)})




    elif 'vrati se na pocetni' in request.POST:
        # Kod koji se izvršava ako je kliknuta dugme da se vrati na pocetni meni
        #Videti kako cemo u zavisnosti od toga koji je role korisnika

        # userName = request.POST['myUsername']
        # role_user = myRole(userName)

        

        # if (role_user!="guest"):
        #     IdKor_current =request.session['IdKor_current']



        #TREBA DODATI I SLANJE SVIH PITANJA SORTIRANO KAKO BI NA NASLOVNOJ strani onaj ko radi mogao da ih obradi
        #TREBA UVESTI IF KAKO BI ZNALI DA LI SE VRACAMO NA mainGuestPage ili na neki drugi page poput modMainPage,regMainPage itd.

        #return render(request, 'EasyQuizzy/mainGuestPage.html',{'role':role_user,'IdKor_current':IdKor_current})
        return redirect('main')



#Funkcija se koristi za ocenjivanje pitanja, ukoliko to korisnik zeli i za prelazak na sledece pitanje, provera da li je korisnik odgovorio na sva pitanja
# kao i prebacivanje na zavrsetak testa i ispis poena i obavestenja ukoliko je korisnik presao na novi nivo!
def grading_question(request):

    type_game = request.session['type_game']

    if request.session['role_user']!="guest":
        if request.method == 'POST':

            choice_button_grade = request.POST.get('dugmad')

            if (choice_button_grade != "preskoci"):
                #Dodati dodavanje Ocene u bazu POSLEE
                #OBAVEZNO DODATIIII

                current_question=json.loads(request.session['current_question'])
                #print("UBACIVANJE OCENE TRENUTNOG PITANJA")
                #print(current_question)

                user_current = Korisnik.objects.get(idkor=request.session['IdKor_current'])
                current_question_database = Pitanje.objects.get(idpit=current_question['idpit'])

                ocena = Ocena()
                ocena.idkor = user_current

                ocena.idpit = current_question_database

                ocena.vrednost_ocene = int(choice_button_grade)
                ocena.save()


                current_question_database.zbir_ocena +=int(choice_button_grade)
                current_question_database.broj_ocena +=1

                sum_grades = current_question_database.zbir_ocena
                number_grades = current_question_database.broj_ocena

                average_grade = sum_grades/(number_grades*1.0)
                current_question_database.prosecna_ocena = average_grade
                current_question_database.save()









    number_current_question = request.session['number_current_question']
    number_questions_chosen = request.session['number_questions_chosen']

    if number_current_question==number_questions_chosen:



        #Resetovanje svega na pocetnu vrednost i cuvanje tih podataka u session-u
        #Mozda ovo i ne mora, ali neka ostane ovako za sada
        number_current_question=0
        request.session['number_current_question'] = number_current_question

        questions_test_current = json.loads(request.session['questions_test_current'])

        while len(questions_test_current)>0:
            questions_test_current.pop(0)

        questions_test_current=[]
        request.session['questions_test_current'] = questions_test_current


        current_question=""
        request.session['current_question'] = current_question

        #Mozda ne treba RESETOVATI number_questions_chosen i category VIDECEMO POSLE!!!
        number_questions_chosen=0
        request.session['number_questions_chosen'] = number_questions_chosen


        category=""
        request.session['category'] = category


        replacement_question = ""

        replacement_question_used = False
        half_half_used = False

        correct_incorrect_layout = []

        request.session['replacement_question'] = replacement_question
        request.session['replacement_question_used'] = replacement_question_used
        request.session['half_half_used'] = half_half_used
        request.session['correct_incorrect_layout'] = correct_incorrect_layout


        request.session['role_user'] = request.session['role']
        role_user = request.session['role_user']

        if (role_user!="guest"):

            IdKor_current = request.session['IdKor_current']



            user = Korisnik.objects.get(idkor=IdKor_current)

            old_level = user.nivo


            number_won_points = request.session['number_won_points']

            won_points_tmp=number_won_points


            user.broj_poena = user.broj_poena + number_won_points

            new_level = (user.broj_poena // 10)+1

            user.nivo=new_level

            user.save()

            user = user.korisnicko_ime

            number_won_points=0
            request.session['number_won_points']=number_won_points



            level_passed=0
            if new_level!=old_level:
                level_passed=1

        else:
            #Ovo je stavljeno da bih znao da je gost u pitanju
            level_passed=-1
            new_level=-1
            number_won_points = request.session['number_won_points']

            won_points_tmp=number_won_points

            number_won_points=0
            request.session['number_won_points']=number_won_points
            user=None

        request.session['level_passed'] = level_passed
        request.session['user'] = user
        request.session['new_level'] = new_level
        request.session['won_points_tmp'] = won_points_tmp

        if type_game == "single":
            return redirect('test_finished_singleplayer_GET')
        else:
            #Videcemo sta cemo ovde
            return render(request, 'EasyQuizzy/test_finished_multiplayer.html', {'user': user,
                                                             'next_level': level_passed,'points_earned':won_points_tmp,'new_level':new_level})

    else:
        #Postavljanje novih vrednosti promenljivih i cuvanje tih podataka u session-u
        number_current_question=number_current_question+1
        request.session['number_current_question']=number_current_question

        questions_test_current=json.loads(request.session['questions_test_current'])
        current_question=questions_test_current.pop(0)
        #print(current_question)

        request.session['questions_test_current'] = json.dumps(questions_test_current,default=decimal_to_float)

        request.session['current_question'] = json.dumps(current_question,default=decimal_to_float)


        # Ovo su odgovori na pitanje izmesani nasumicno

        correct_incorrect_layout_answers = [current_question['tacan_odgovor'], current_question['netacan1'],
                                            current_question['netacan2'], current_question['netacan3']]
        random.shuffle(correct_incorrect_layout_answers)

        request.session['correct_incorrect_layout_answers'] = correct_incorrect_layout_answers

        # Ovi indikatori stoje kako bi znao koji je odgovor tacan a koji netacan
        correct_incorrect_layout_indicators = []

        for ans in correct_incorrect_layout_answers:
            if ans == current_question['tacan_odgovor']:
                correct_incorrect_layout_indicators.append(1)
            else:
                correct_incorrect_layout_indicators.append(0)

        # Ovo se koristi kako bi znao da li da stavis pitanje u prvi <tr> ili u drugi <tr> kako bi imao lepo rasporedjeno 2 dugmeta po redu,kao u prototipu
        # 0 i 1 idu u prvi <tr> 2 i 3 idu u drugi <tr>

        correct_incorrect_rows_table = [0, 1, 2, 3]

        # Ovo je sve zipovano,sto znaci da posto imamo 3 liste i sve 3 imaju isti broj elementa (po 4) sada zapravo imas 4 tupla sa po 3 clana
        # jedan tuple od 4 izgleda ovako (tekst_pitanja,indikator_tacnosti,redni_broj_koristi_se_za_<tr>)
        # Lista je napravljena kako bi mogao vise puta da iteriras kroz listu u html-u,da je bez list() mogao bi samo jednom da prodjes kroz listu
        # ovako ces moci 2 puta taman prodjes jednom za svaki row tabele (<tr>)!

        correct_incorrect_data = list(
            zip(correct_incorrect_layout_answers, correct_incorrect_layout_indicators, correct_incorrect_rows_table))
        request.session['correct_incorrect_data'] = json.dumps(correct_incorrect_data, default=decimal_to_float)


        if type_game == "single":

            #SAMO ZA PROBU DA LI RADI

            #return render(request, 'EasyQuizzy/question_grading.html', {'question_text_content':current_question['tekst_pitanja'],
                                                             # 'correct_incorrect_data': correct_incorrect_data})

            return redirect('grading_question_GET')
        else:
            #Videcemo sta cemo ovde
            return render(request, 'EasyQuizzy/test_multiplayer.html',
                          {'korIme': request.session['korIme'],
                           'number_current_question': request.session['number_current_question'],
                           'question_text_content': current_question['tekst_pitanja'],
                           'correct_incorrect_data': correct_incorrect_data,
                           'half_half_used': request.session['half_half_used'],
                           'replacement_question_used': request.session['replacement_question_used'],
                           'disabled': [4, 4]})



#Koristi se samo kako bi moglo da se spreci da se desi nesto sto ne bi trebalo kada se uradi RELOAD stranice
def grading_question_GET(request):


    current_question = json.loads(request.session['current_question'])
    correct_incorrect_data = json.loads(request.session['correct_incorrect_data'])

    return render(request, 'EasyQuizzy/test_singleplayer.html',
                  {'korIme': request.session['korIme'],
                   'number_current_question': request.session['number_current_question'],
                   'question_text_content': current_question['tekst_pitanja'],
                   'correct_incorrect_data': correct_incorrect_data,
                   'half_half_used': request.session['half_half_used'],
                   'replacement_question_used': request.session['replacement_question_used'],
                   'disabled': [None, None]})

#Koristi se samo kako bi moglo da se spreci da se desi nesto sto ne bi trebalo kada se uradi RELOAD stranice
def test_finished_singleplayer_GET(request):
    level_passed = request.session['level_passed']
    user = request.session['user']
    new_level = request.session['new_level']
    won_points_tmp = request.session['won_points_tmp']

    return render(request, 'EasyQuizzy/test_finished_singleplayer.html', {'user': user,
                                                                          'next_level': level_passed,
                                                                          'points_earned': won_points_tmp,
                                                                          'new_level': new_level})