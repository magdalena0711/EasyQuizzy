

from .models import *
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
import base64
from . import views_guest_and_reg
from . import stickers

'''
funkcija koja vraća stikere za levi i desni navigacioni bar svake stranice za različite vrste korisnika
'''
def get_stickers(request):

    my_username = request.user.username

    my_role = views_guest_and_reg.myRole(my_username)

    if my_role == 1:
        return stickers.leftModerator, stickers.rightModerator
    elif my_role == 2:
        return stickers.leftAdmin, stickers.rightAdmin
    elif my_role == 0:
        return stickers.leftRegistered, stickers.rightRegistered
    return stickers.leftGuest, stickers.rightGuest
'''
funkcija koja vraća listu koja sadrži sve korisnike
svaki korisnik je predstavljen listom koja sadrži podatke o korisničkom imenu, imenu, prezimenu, email-u, polu i vrsti korisnika
'''
def get_all_users():
    
    admins = Administrator.objects.select_related('idkor')
    moderators = Moderator.objects.select_related('idkor')
    users = RegistrovaniKorisnik.objects.select_related('idkor')

    all_users = list()
    types = ['admin', 'moderator', 'korisnik']
    users_objects = [admins, moderators, users]

    i = 0
    for tp in types:
        for user in users_objects[i]:
            if user.idkor.vazeci == 1:
                user_list = list()
                user_list.append(user.idkor.korisnicko_ime)
                user_list.append(user.idkor.ime)
                user_list.append(user.idkor.prezime)
                user_list.append(user.idkor.email)
                user_list.append(user.idkor.pol)
                user_list.append(tp)
                all_users.append(user_list)
        i += 1

    return all_users

'''
funkcija vraća stranicu koja izlistava sve korisnike
'''
def show_users(request):

    template = loader.get_template('EasyQuizzy/add_delete_user.html')

    left, right = get_stickers(request)
    
    all_users = get_all_users()

    context = {
        'all_users': all_users,
        'left': left,
        'right': right
    }
    return HttpResponse(template.render(context, request))


'''
funkcija obrađuje AJAX zahtev za brisanje korisnika
proverava da li korisnik postoji i postavlja mu polje "vazeci" na 0
'''
def delete_user(request):
    data = request.body.decode()
    username = data.split("=")[1]
    user_list = Korisnik.objects.filter(korisnicko_ime = username).all()
    successful = False
    if len(user_list) == 0:
        
        msg = "Ne postoji korisnik koga želite da obrišete"
    else:
        successful = True
        user = user_list[0]
        user.vazeci = 0
        user.save()
        msg = "Uspešno ste izvršili brisanje korisnika"

    return JsonResponse({'message' : msg, 'successful': successful})


'''
funkcija vraća listu rečnika
rečnik se sastoji od tri elementa, gde su ključevi imena kategorija, dok su vrednosti binarni prikazi slika
'''
def get_category_images():
    #uzimanje slika svih kategorija iz baze
    category_images = Kategorija.objects.values('slika', 'naziv').all()
    blobs = list()
    for i in range(0, len(category_images), 3):
        threes = dict()
        threes[category_images[i]['naziv']] = (base64.b64encode(category_images[i]['slika']).decode('utf-8'))
        if i+1 < len(category_images):
            threes[category_images[i+1]['naziv']] = (base64.b64encode(category_images[i+1]['slika']).decode('utf-8'))
        if i+2 < len(category_images):
            threes[category_images[i+2]['naziv']] = (base64.b64encode(category_images[i+2]['slika']).decode('utf-8'))
        blobs.append(threes)
    return blobs

'''
funkcija vraća sva pitanja određenog tipa
2 - predložena
1 - odobrena
0 - ubačena
'''
def get_questions(question_status):
    #uzimanje svih odobrenih pitanja
    permitted_questions = Pitanje.objects.values('tekst_pitanja').filter(status = question_status).all()
    questions = dict()
    
    for i in range(len(permitted_questions)):
        questions[i+1] = permitted_questions[i]['tekst_pitanja']
    return questions


'''
funkcija vraća stranicu za izmenu i dodavanje pitanja
'''
def adding_questions(request):
    template = loader.get_template('EasyQuizzy/adding_questions.html')

    left, right = get_stickers(request)
    
    context = {
        'categories': get_category_images(),
        'permitted': get_questions(1),
        'message': '',
        'messageChange': '',
        'messagePermitted': '',
        'left': left,
        'right': right
    }

    return HttpResponse(template.render(context, request)) 

'''
funkcija dodaje novo pitanje prosleđeno putem forme
proverava se da li pitanje sa unetim tekstom već postoji
'''  
def add_new_question(request):
    template = loader.get_template('EasyQuizzy/adding_questions.html')

    left, right = get_stickers(request)


    context = {
        'categories': get_category_images(),
        'permitted': get_questions(1),
        'messageChange': '',
        'messagePermitted': '',
        'left': left,
        'right': right
    }

    if len(request.POST.keys()) != 8:
        msg = 'Niste popunili sva polja!'
    else:
        category = request.POST['category']
        text = request.POST['question']
        weight = request.POST['weight']
        correct = request.POST['correct']
        incorrect1 = request.POST['incorrect1']
        incorrect2 = request.POST['incorrect2']
        incorrect3 = request.POST['incorrect3']

        
        question = Pitanje.objects.filter(tekst_pitanja = text).all()
        if len(question) > 0:
            msg = "Pitanje sa datim tekstom već postoji!"
        else:
            id_cat = Kategorija.objects.filter(naziv = category).all()[0]
            
            new_question = Pitanje()
            new_question.idkat = id_cat
            new_question.tekst_pitanja = text
            new_question.tezina_pitanja = weight
            new_question.tacan_odgovor = correct
            new_question.netacan1 = incorrect1
            new_question.netacan2 = incorrect2
            new_question.netacan3 = incorrect3
            new_question.status = 0
            new_question.zbir_ocena = 0
            new_question.prosecna_ocena = 0
            new_question.broj_ocena = 0
            new_question.save()
            msg = "Pitanje je uspešno ubačeno u bazu!"
    
    context['message'] = msg

    return HttpResponse(template.render(context, request)) 

def get_questions_category(request):
    category = request.GET['name']
    
    cat_id = Kategorija.objects.filter(naziv = category).all()
    cat_id = cat_id[0].idkat
    
    questions = Pitanje.objects.values('tekst_pitanja', 'tezina_pitanja', 'tacan_odgovor', 'netacan1', 'netacan2', 'netacan3', 'idpit').filter(idkat = cat_id).filter(status = 0).all()
    
    quest_dict = dict()

    for i in range(len(questions)):
        info = list()
        info.append(questions[i]['tekst_pitanja'])
        info.append(questions[i]['tezina_pitanja'])
        info.append(questions[i]['tacan_odgovor'])
        info.append(questions[i]['netacan1'])
        info.append(questions[i]['netacan2'])
        info.append(questions[i]['netacan3'])
        info.append(questions[i]['idpit'])
        quest_dict[i+1] = info

    return JsonResponse({'questions' : json.dumps(quest_dict)})

def question_update(question, text, weight, correct, incorrect1, incorrect2, incorrect3):
        question.tekst_pitanja = text
        question.tezina_pitanja = weight
        question.tacan_odgovor = correct
        question.netacan1 = incorrect1
        question.netacan2 = incorrect2
        question.netacan3 = incorrect3
        question.save()

def change_question(request):
    template = loader.get_template('EasyQuizzy/adding_questions.html')

    if len(request.POST.keys()) != 8:
        msg = 'Niste popunili sva polja!'
    else:
        id = request.POST['id']
        text = request.POST['question']
        weight = request.POST['weight']
        correct = request.POST['correct']
        incorrect1 = request.POST['incorrect1']
        incorrect2 = request.POST['incorrect2']
        incorrect3 = request.POST['incorrect3']

        id = int(id)
        question = Pitanje.objects.filter(tekst_pitanja = text).all()
        if question[0].idpit != id:
            msg = "Pitanje sa datim tekstom već postoji!"
        else:
            change = Pitanje.objects.filter(idpit = id).all()
            change = change[0]
            question_update(change, text, weight, correct, incorrect1, incorrect2, incorrect3)
            msg = "Uspešno ste izvršili izmenu pitanja!"

    left, right = get_stickers(request)

    context = {
        'categories': get_category_images(),
        'permitted': get_questions(1),
        'message': '',
        'messagePermitted': '',
        'messageChange': msg,
        'left': left,
        'right': right
    }
    

    return HttpResponse(template.render(context, request))

def add_permitted_question(request):
    template = loader.get_template('EasyQuizzy/adding_questions.html')

    
    if len(request.POST.keys()) != 8 or request.POST['question'] == '':
        msg = 'Niste popunili sva polja!'
    else:
        category = request.POST['category']
        text = request.POST['question']
        weight = request.POST['weight']
        correct = request.POST['correct']
        incorrect1 = request.POST['incorrect1']
        incorrect2 = request.POST['incorrect2']
        incorrect3 = request.POST['incorrect3']

        question = Pitanje.objects.filter(tekst_pitanja = text).all()
        question = question[0]
        cat = Kategorija.objects.filter(naziv = category).all()
        cat = cat[0]
        question.idkat = cat
        question.status = 0
        question_update(question, text, weight, correct, incorrect1, incorrect2, incorrect3)
        msg = "Uspešno ste izvršili dodavanje pitanja iz skupa odobrenih!"

    left, right = get_stickers(request)
    
    context = {
        'categories': get_category_images(),
        'permitted': get_questions(1),
        'messageChange': '',
        'message': '',
        'messagePermitted': msg,
        'left': left,
        'right': right
    }

    return HttpResponse(template.render(context, request))

def show_categories(request):
    template = loader.get_template('EasyQuizzy/categories.html')

    images = get_category_images()

    left, right = get_stickers(request)

    context = {
        'images': images,
        'left': left,
        'right': right
    }

    return HttpResponse(template.render(context, request))

def add_moderator(request):
    data = request.body.decode()
    username = data.split("=")[1]
    user_list = Korisnik.objects.filter(korisnicko_ime = username).filter(vazeci = 1).all()
    successful = False

    if len(user_list) == 0:
        msg = "Korisnik sa unetim korisničkim imenom ne postoji"
    else:
        user = user_list[0]
        id = user.idkor
        registered_user = RegistrovaniKorisnik.objects.filter(idkor = id).all()
        if len(registered_user) > 0:
            registered_user = registered_user[0]
            registered_user.delete()
            moderator = Moderator()
            moderator.idkor = user
            moderator.save()
            successful = True
            msg = 'Uspešno ste izvršili postavljanje moderatora'
        else:
            msg = 'Izabrani korisnik već ima ulogu moderatora'
        
    return JsonResponse({'message' : msg, 'successful': successful})

def to_permit(request):
    template = loader.get_template('EasyQuizzy/question_permission.html')

    left, right = get_stickers(request)

    context = {
        'questions': get_questions(2),
        'left': left,
        'right': right
    }
    return HttpResponse(template.render(context, request))

def add_to_permitted(request):
    template = loader.get_template('EasyQuizzy/question_permission.html')

    text_list = request.POST.getlist('checkbox')
    
    for text in text_list:
        question = Pitanje.objects.filter(tekst_pitanja = text).first()
        if "permit" in request.POST:
            question.status = 1
            question.save()
        else:
            question.delete()

    left, right = get_stickers(request)
    
    context = {
        'questions': get_questions(2),
        'left': left,
        'right': right
    }
    return HttpResponse(template.render(context, request))

def changing_categories_page(request):
    template = loader.get_template('EasyQuizzy/adding_categories.html')

    left, right = get_stickers(request)
    images = get_category_images()

    context = {
        'images': images,
        'messageChange': '',
        'left': left,
        'right': right,
        'messageQu': '',
        'messageCat': ''
    }

    return HttpResponse(template.render(context, request))

def change_existing_category(request):
    template = loader.get_template('EasyQuizzy/adding_categories.html')

    left, right = get_stickers(request)
    print(request.FILES)

    msg = ''
    if 'file' in request.FILES and request.POST['firstName'] != '':
        current_name = request.POST['firstName']
        to_change = Kategorija.objects.filter(naziv = current_name).all()
        to_change = to_change[0]
        #konvertovanje u binarni fajl
        to_change.slika = request.FILES['file'].read()
        to_change.save()
        msg = 'Promena je uspešno napravljena'
    if request.POST['category'] != '' and request.POST['firstName'] != '':
        new_name = request.POST['category']
        existing = Kategorija.objects.filter(naziv = new_name).all()
        if len(existing) == 0:
            current_name = request.POST['firstName']
            to_change = Kategorija.objects.filter(naziv = current_name).all()
            to_change = to_change[0]
            to_change.naziv = new_name
            to_change.save()
            msg = 'Promena je uspešno napravljena'
        else:
            msg = 'Kategorija sa datim nazivom već postoji'
    
    images = get_category_images()
    context = {
        'images': images,
        'messageChange': msg,
        'left': left,
        'right': right,
        'messageQu': '',
        'messageCat': ''
    }
   
    return HttpResponse(template.render(context, request))

def add_question_for_category(request):
    template = loader.get_template('EasyQuizzy/adding_categories.html')

    left, right = get_stickers(request)

    text = request.POST['text']
    weight = request.POST.get('weight', '')
    correct = request.POST['correct']
    incorrect1 = request.POST['incorrect1']
    incorrect2 = request.POST['incorrect2']
    incorrect3 = request.POST['incorrect3']
    values = [text, weight, correct, incorrect1, incorrect2, incorrect3]

    images = get_category_images()
    context = {
        'images': images,
        'messageChange': '',
        'left': left,
        'right': right,
        'messageQu': '',
        'messageCat': ''
    }

    if text == '' or weight == '' or correct == '' or incorrect1 == '' or incorrect2 == '' or incorrect3 == '':
        msg = 'Niste uneli sva polja'
        context['messageQu'] = msg
        return HttpResponse(template.render(context, request))

    response = HttpResponse(template.render(context, request))
    print(request.COOKIES)
    if 'pitanja' not in request.COOKIES:
        questions = dict()
        questions['pitanja'] = list()
        questions['pitanja'].append(values)
        response.set_cookie('pitanja', json.dumps(questions))
    else:
        questions = json.loads(request.COOKIES['pitanja'])
        questions['pitanja'].append(values)
        response.set_cookie('pitanja', json.dumps(questions))

    context['messageQu'] = 'Uspešno ste dodali pitanje'

    return response

def add_new_category(request):
    template = loader.get_template('EasyQuizzy/adding_categories.html')

    left, right = get_stickers(request)

    context = {
        'images': get_category_images(),
        'messageChange': '',
        'left': left,
        'right': right,
        'messageQu': ''
    }

    new_name = request.POST['newCatName']
    if new_name == '' or 'newCatFile' not in request.FILES:
        context['messageCat'] = 'Niste uneli sva polja'
        return HttpResponse(template.render(context, request))
    
    if 'pitanja' not in request.COOKIES:
        context['messageCat'] = 'Niste uneli minimum pet novih pitanja'
        return HttpResponse(template.render(context, request))
    
    questions = json.loads(request.COOKIES['pitanja'])
    if len(questions['pitanja']) < 5:
        context['messageCat'] = 'Niste uneli minimum pet novih pitanja'
        return HttpResponse(template.render(context, request))

    for question in questions['pitanja']:
        existing = Pitanje.objects.filter(tekst_pitanja = question[0]).first()
        print(existing)
        if existing != None:
            questions['pitanja'].remove(question)

    if len(questions['pitanja']) < 5:
        more = 5 - len(questions['pitanja'])
        context['messageCat'] = f'Neka pitanja već postoje u bazi; unesite još {more} pitanja'
        response = HttpResponse(template.render(context, request))
        response.set_cookie('pitanja', json.dumps(questions))
        return response
    
    existing_cat = Kategorija.objects.filter(naziv = new_name).first()
    if existing_cat != None:
        context['messageCat'] = 'Kategorija sa datim nazivom već postoji'
        return HttpResponse(template.render(context, request))


    new_category = Kategorija()
    new_category.naziv = new_name
    new_category.slika = request.FILES['newCatFile'].read()
    new_category.save()
    
    for question in questions['pitanja']:
        print(question)
        new_question = Pitanje(status=0, zbir_ocena=0, prosecna_ocena=0, broj_ocena=0)
        new_question.idkat = Kategorija.objects.filter(naziv = new_name).first()
        question_update(new_question, question[0], question[1], question[2], question[3], question[4], question[5])
        print(new_question)
    
    

    context['messageCat'] = 'Kategorija je uspešno dodata'
    context['images'] = get_category_images()

    response = HttpResponse(template.render(context, request))
    response.delete_cookie('pitanja')
    return response




    