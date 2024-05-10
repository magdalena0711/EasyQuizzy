from .models import *
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import json
import base64

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


def show_users(request):

    template = loader.get_template('EasyQuizzy/add_delete_user.html')
    
    all_users = get_all_users()

    context = {
        'all_users': all_users
    }
    return HttpResponse(template.render(context, request))

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

def get_permitted_questions():
    #uzimanje svih odobrenih pitanja
    permitted_questions = Pitanje.objects.values('tekst_pitanja').filter(status = 1).all()
    questions = dict()
    
    for i in range(len(permitted_questions)):
        questions[i+1] = permitted_questions[i]['tekst_pitanja']
    return questions


def adding_questions(request):
    template = loader.get_template('EasyQuizzy/adding_questions.html')
    
    context = {
        'categories': get_category_images(),
        'permitted': get_permitted_questions(),
        'message': '',
        'messageChange': '',
        'messagePermitted': ''
    }

    return HttpResponse(template.render(context, request)) 
    
def add_new_question(request):
    template = loader.get_template('EasyQuizzy/adding_questions.html')


    context = {
        'categories': get_category_images(),
        'permitted': get_permitted_questions(),
        'messageChange': '',
        'messagePermitted': ''
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

    id = request.POST['id']
    text = request.POST['question']
    weight = request.POST['weight']
    correct = request.POST['correct']
    incorrect1 = request.POST['incorrect1']
    incorrect2 = request.POST['incorrect2']
    incorrect3 = request.POST['incorrect3']

    context = {
        'categories': get_category_images(),
        'permitted': get_permitted_questions(),
        'message': '',
        'messagePermitted': ''
    }

    id = int(id)
    question = Pitanje.objects.filter(tekst_pitanja = text).all()
    if question[0].idpit != id:
        msg = "Pitanje sa datim tekstom već postoji!"
    else:
        change = Pitanje.objects.filter(idpit = id).all()
        change = change[0]
        question_update(change, text, weight, correct, incorrect1, incorrect2, incorrect3)
        msg = "Uspešno ste izvršili izmenu pitanja!"

    context['messageChange'] = msg

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
    
    context = {
        'categories': get_category_images(),
        'permitted': get_permitted_questions(),
        'messageChange': '',
        'message': '',
        'messagePermitted': msg
    }

    return HttpResponse(template.render(context, request))

