#Elena Savić 21/0332
#Petar Milojević 21/0336
#Ilija Miletić 21/0335
#Magdalena Obradović 21/0304

from django.shortcuts import render
from django_redis import get_redis_connection
import json
from .models import *
import random
from django.http import JsonResponse
import threading
import urllib.parse

# mutex je semafor koji se koristi za sinhronizaciju vise igraca (consumera)
mutex = threading.Semaphore()

def correct_answer(text):
    """
    Pomoćna funkcija koja vraća tačan odgovor na pitanje na osnovu zadatog teksta
    """
    question = Pitanje.objects.filter(tekst_pitanja = text).first()
    return question.tacan_odgovor

def initialize():
    """
    Funkcija za inicijalizaciju, vraća sva pitanja koja će se koristiti tokom testa i sve tačne odgovore
    """
    questions = list()
    allQuestions = list(Pitanje.objects.filter(status=0).all())
    random.shuffle(allQuestions)
    """
    Uzimamo sva pitanja i mešamo ih da ne bi uvek dobijali ista pitanja
    """

    answers = list()
    correct_incorrect = list()
    correct_incorrect_rows_table = [0, 1, 2, 3]

    for i in range(12):
        """
        Petlja se vrti 12 puta, jer nam je 12 pitanja potrebno
        10 klasičnih i po jedno za svaku zamenu pitanja, jer svaki igrač može da zameni pitanje po jednom
        """
        questions.append(allQuestions[i].tekst_pitanja)
        answers.append([allQuestions[i].tacan_odgovor, allQuestions[i].netacan1, allQuestions[i].netacan2, allQuestions[i].netacan3])
        random.shuffle(answers[i])

        indicators = []
        """
        Indikatori služe da se tačni odgovori promešaju, da ne bi uvek prvi odgovor bio tačan
        """
        for answer in answers[i]:
            if answer == allQuestions[i].tacan_odgovor:
                indicators.append(1)
            else:
                indicators.append(0)
        correct_incorrect.append(list(zip(answers[i], indicators, correct_incorrect_rows_table)))

    """
    current_number je broj trenutnog pitanja
    """
    current_number = 0
    return current_number, correct_incorrect, questions


def next_question(request, room_name):
    """
    exchange_question predstavlja kod za skup u redisu koji koristimo prilikom zamene pitanja
    """
    exchange_question = room_name + "replace"
    """
    Igrač koji uđe u ovu funkciju, zauzima bravu jer je moguće da da naredni igrač
    pročuta current_number pre nego što ga prvi promeni
    """
    mutex.acquire()
    keySet = 'abc' + room_name + 'abc'
    """
    
    """
    redis_conn = get_redis_connection("default")
    """
    Ostvarujemo konekciju sa redisom
    """
    current_number = int(redis_conn.hget(room_name,"current_number"))
    
    if (len(redis_conn.smembers(keySet)) == 0):
        """
        Ako sam prvi igrač koji je ušao u ovu funkciju
        U skup za zamenu pitanja dodajem broj 9 - jer će se uzeti 10. pitanje prilikom zamene
        U drugi skup dodajemo trenutni broj pitanja, zatim ga povećavamo
        """
        redis_conn.sadd(exchange_question, 9)
        redis_conn.sadd(keySet, current_number)
        current_number = current_number + 1
        redis_conn.hset(room_name, "current_number", current_number)
    else: 
        """
        Drugi igrač koji uđe u ovu funkciju, iz skupa briše trenutni broj pitanja, smanjen za jedan
        Jer ga je prvi igrač povećao
        """
        redis_conn.srem(keySet,current_number -1)
    """
    Mutex puštamo, jer sada igrači istovremeno mogu da se nalaze u ostatku funkcije, bez problema
    Tj. više ne dolazi do promene koja može da utiče na saigrača
    """
    mutex.release()
    questions_dict = json.loads(redis_conn.hget(room_name, "questions"))
    questions = questions_dict['questions']
    correct_incorrect_dict = json.loads(redis_conn.hget(room_name, "correct_incorrect_data"))
    correct_incorrect_list = correct_incorrect_dict['answers']
    
    return render(request, 'EasyQuizzy/test_multiplayer.html',
                  {'korIme': request.user.username,
                   'number_current_question': current_number,
                   'question_text_content': questions[current_number-1] ,
                   'correct_incorrect_data': correct_incorrect_list[current_number-1],
                   'half_half_used': '',
                   'replacement_question_used': '',
                   'disabled': [4, 4]})


def jump_next(request):
    """
    Funkcija za prelazak na sledeće pitanje
    Radi po istom principu kao i funkcija next_question
    Ima i proveru da li smo došli do poslednjeg pitanja
    U slučaju da nismo, u js ćemo za vrednost done poslati negativnu vrednost, pa ćemo tako znati da još nismo doši do poslednjeg pitanja
    Kada se radi o 11. pitanju, znamo da je kraj
    Čak i kada korisnici zamene pitanja, i dalje će 11. pitanje biti naznaka za kraj
    Jer će im prilikom zamene, biti dato 10. i 11. pitanje (ako brojimo od 0), tj 11. i 12.
    """
    mutex.acquire()
    data = request.body.decode()

    print("usao u jumpNext")
    room_name = data.split("=")[1]
    keySet = 'abc' + room_name + 'abc'
    redis_conn = get_redis_connection("default")
    current_number = int(redis_conn.hget(room_name,"current_number"))
    
    print(redis_conn.smembers(keySet))
    if (len(redis_conn.smembers(keySet)) == 0):
        redis_conn.sadd(keySet, current_number)
        current_number = current_number + 1
        redis_conn.hset(room_name, "current_number", current_number)
    else: 
        redis_conn.srem(keySet,current_number-1 )     
        room_group_name = 'quiz_' + room_name
        allMembers = redis_conn.hgetall(room_group_name)
        for key, val in allMembers.items():
            redis_conn.hdel(room_group_name, key.decode('utf-8'))
        allMembers = redis_conn.hgetall(room_group_name)
    mutex.release()
    if current_number == 11:
        return JsonResponse({'done': True})
    questions_dict = json.loads(redis_conn.hget(room_name, "questions"))
    questions = questions_dict['questions']
    correct_incorrect_dict = json.loads(redis_conn.hget(room_name, "correct_incorrect_data"))
    correct_incorrect_list = correct_incorrect_dict['answers']
    answer_list = list()
    for item in correct_incorrect_list[current_number-1]:
        answer_list.append(item[0])

    
    return JsonResponse({'current_number': current_number, 'question': questions[current_number-1], 'answers': answer_list, 'done' : False})


def done_multiplayer(request):

    """
    Funkcija koja obrađuje kraj partije
    Dohvata trenutnog igrača i ako je dostigao određeni broj poena, povećava mu nivo
    """
    user = Korisnik.objects.get(korisnicko_ime = request.user.username)
    old_level = user.nivo
    number_won_points = request.POST['points']
    won_points_tmp = number_won_points
    user.broj_poena = user.broj_poena + int(number_won_points)
    new_level = (user.broj_poena // 10)+1
    user.nivo=new_level
    
    user.save()
    return render(request, 'EasyQuizzy/test_finished_multiplayer.html',{})


def get_correct(request):
    """
    Funkcija koja u json formatu šalje tačan odgovor na dobijeno pitanje
    """
    data = request.body.decode('utf-8')
    textQuestion = data.split("=")[1]
    textQuestion = urllib.parse.unquote(textQuestion)
    correct_answer_send = correct_answer(textQuestion)

    return JsonResponse({'correct': correct_answer_send})



