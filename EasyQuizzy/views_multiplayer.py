from django.shortcuts import render
from django_redis import get_redis_connection
import json
from .models import *
import random
from django.http import JsonResponse
import threading
import urllib.parse

mutex = threading.Semaphore()

def correct_answer(text):
    question = Pitanje.objects.filter(tekst_pitanja = text).first()
    return question.tacan_odgovor

def initialize():
    questions = list()
    print("usao u init")

    allQuestions = list(Pitanje.objects.filter(status=0).all())
    #print(allQuestions)
    random.shuffle(allQuestions)

    answers = list()
    correct_incorrect = list()
    correct_incorrect_rows_table = [0, 1, 2, 3]


    for i in range(12):

        questions.append(allQuestions[i].tekst_pitanja)
        answers.append([allQuestions[i].tacan_odgovor, allQuestions[i].netacan1, allQuestions[i].netacan2, allQuestions[i].netacan3])
        random.shuffle(answers[i])

        indicators = []
        for answer in answers[i]:
            if answer == allQuestions[i].tacan_odgovor:
                indicators.append(1)
            else:
                indicators.append(0)
        correct_incorrect.append(list(zip(answers[i], indicators, correct_incorrect_rows_table)))



    current_number = 0

    #correct_incorrect_data = list(zip(answers, indicators, correct_incorrect_rows_table))

    return current_number, correct_incorrect, questions


def next_question(request, room_name):
    exchange_question = room_name + "replace"
    mutex.acquire()
    keySet = 'abc' + room_name + 'abc'

    #print(f'ROOM {room_name}')
    redis_conn = get_redis_connection("default")
    current_number = int(redis_conn.hget(room_name,"current_number"))
    
    if (len(redis_conn.smembers(keySet)) == 0):
        redis_conn.sadd(keySet, current_number)
        current_number = current_number + 1
        redis_conn.hset(room_name, "current_number", current_number)
    else: 
        redis_conn.sadd(exchange_question, 9)
        redis_conn.srem(keySet,current_number -1)
    
    mutex.release()
    #print(len(redis_conn.smembers(keySet)))
    #print(current_number)
    questions_dict = json.loads(redis_conn.hget(room_name, "questions"))
    questions = questions_dict['questions']
    #print(current_number)
    correct_incorrect_dict = json.loads(redis_conn.hget(room_name, "correct_incorrect_data"))
    correct_incorrect_list = correct_incorrect_dict['answers']
    #print(correct_incorrect_dict)
    # print(questions)
    #print(redis_conn.hmget("data", "questions"))
    
    return render(request, 'EasyQuizzy/test_multiplayer.html',
                  {'korIme': request.user.username,
                   'number_current_question': current_number,
                   'question_text_content': questions[current_number-1] ,
                   'correct_incorrect_data': correct_incorrect_list[current_number-1],
                   'half_half_used': '',
                   'replacement_question_used': '',
                   'disabled': [4, 4]})


def jump_next(request):
    mutex.acquire()
    data = request.body.decode()

    print("usao u jumpNext")
    room_name = data.split("=")[1]
    keySet = 'abc' + room_name + 'abc'
    redis_conn = get_redis_connection("default")
    current_number = int(redis_conn.hget(room_name,"current_number"))
    #print(current_number)
    
    print(redis_conn.smembers(keySet))
    if (len(redis_conn.smembers(keySet)) == 0):
        redis_conn.sadd(keySet, current_number)
        current_number = current_number + 1
        redis_conn.hset(room_name, "current_number", current_number)
    else: 
        redis_conn.srem(keySet,current_number-1 )
        
        room_group_name = 'quiz_' + room_name
        allMembers = redis_conn.hgetall(room_group_name)
        print(f'ALL MEMBERS{allMembers}')
        for key, val in allMembers.items():
            redis_conn.hdel(room_group_name, key.decode('utf-8'))
        allMembers = redis_conn.hgetall(room_group_name)
        print(f'DELETED {allMembers}')
        print(f"AFTER {len(allMembers)}")
    mutex.release()
    
    print(f'CURRENT NUMBER {current_number}')
    #print("povecao broj")
    if current_number == 11:
        return JsonResponse({'done': True})
    questions_dict = json.loads(redis_conn.hget(room_name, "questions"))
    questions = questions_dict['questions']
    #print(current_number)
    correct_incorrect_dict = json.loads(redis_conn.hget(room_name, "correct_incorrect_data"))
    correct_incorrect_list = correct_incorrect_dict['answers']
    answer_list = list()
    for item in correct_incorrect_list[current_number-1]:
        answer_list.append(item[0])
    #print(answer_list)
    
    return JsonResponse({'current_number': current_number, 'question': questions[current_number-1], 'answers': answer_list, 'done' : False})


def done_multiplayer(request):
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
    data = request.body.decode('utf-8')
    
    print(data)

    print("usao u get_correct")
    textQuestion = data.split("=")[1]
    textQuestion = urllib.parse.unquote(textQuestion)
    print(textQuestion)
    correct_answer_send = correct_answer(textQuestion)

    return JsonResponse({'correct': correct_answer_send})



