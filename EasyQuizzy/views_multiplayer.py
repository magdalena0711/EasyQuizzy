from django.shortcuts import render
from django_redis import get_redis_connection
import json
from .models import *
import random



def initialize():
    questions = list()
    print("usao u init")

    allQuestions = list(Pitanje.objects.filter(status=0).all())
    #print(allQuestions)
    random.shuffle(allQuestions)

    answers = list()
    correct_incorrect = list()
    correct_incorrect_rows_table = [0, 1, 2, 3]


    for i in range(11):

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
    redis_conn = get_redis_connection("default")
    current_number = int(redis_conn.hget("data","current_number"))
    current_number = current_number + 1
    questions_dict = json.loads(redis_conn.hget("data", "questions"))
    questions = questions_dict['questions']
    #print(current_number)
    correct_incorrect_dict = json.loads(redis_conn.hget("data", "correct_incorrect_data"))
    correct_incorrect_list = correct_incorrect_dict['answers']
    #print(correct_incorrect_dict)
    # print(questions)
    #print(redis_conn.hmget("data", "questions"))
    return render(request, 'EasyQuizzy/test_multiplayer.html',
                  {'korIme': '',
                   'number_current_question': current_number,
                   'question_text_content': questions[current_number-1] ,
                   'correct_incorrect_data': correct_incorrect_list[current_number-1],
                   'half_half_used': '',
                   'replacement_question_used': '',
                   'disabled': [4, 4]})


