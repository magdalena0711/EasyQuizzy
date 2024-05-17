#Ilija Miletić 2021/0335
import json
import random

from .models import *
from django.shortcuts import render, redirect
from .viewsPetar import grading_question


def answer(request):
    if request.method == "POST":

        choice = request.POST.get("answer_choice")
        answer_text = request.POST.get("answer_text" + str(choice))
        question_text = request.POST.get("question_text")
        question = Pitanje.objects.get(tekst_pitanja=question_text)

        if answer_text == question.tacan_odgovor:
            request.session['number_won_points'] += 1

        answers = [request.POST.get("answer_text" + str(0)), request.POST.get("answer_text" + str(1)),
                   request.POST.get("answer_text" + str(2)), request.POST.get("answer_text" + str(3))]

        for i in range(4):
            if answers[i] == question.tacan_odgovor:
                correct = i
                break

        return render(request, "EasyQuizzy/answered_singleplayer.html",
                      {'korIme': request.session['korIme'],
                       'number_current_question': request.session['number_current_question'],
                       'question_text_content': question_text,
                       'answers': answers,
                       'half_half_used': request.session['half_half_used'],
                       'replacement_question_used': request.session['replacement_question_used'],
                       'choice': choice, 'correct': correct})


def load_grading(request):
    if request.method == "POST":

        if (request.session['role_user'] != 'guest'):
            return render(request, "EasyQuizzy/question_grading.html",
                          {"question_text_content": request.POST.get("question_text")})
        else:
            return redirect(grading_question)


def fifty_fifty(request):
    if request.method == "POST":

        request.session['half_half_used'] = True

        question_text = request.POST.get("question_text")
        correct_answer = Pitanje.objects.get(tekst_pitanja=question_text).tacan_odgovor

        answers = [request.POST.get("answer_text" + str(0)), request.POST.get("answer_text" + str(1)),
                   request.POST.get("answer_text" + str(2)), request.POST.get("answer_text" + str(3))]

        incorrect = []
        for i in range(4):
            if answers[i] != correct_answer:
                incorrect.append(i)

        disable1 = random.randint(0, 1)
        disable2 = (disable1 + 1 + random.randint(0, 1)) % 3
        disable1 = incorrect[disable1]
        disable2 = incorrect[disable2]

        correct_incorrect_data = list(zip(answers, [0, 0, 0, 0]))

        return render(request, "EasyQuizzy/test_singleplayer.html",
                      {'korIme': request.session['korIme'],
                       'number_current_question': request.session['number_current_question'],
                       'question_text_content': question_text,
                       'correct_incorrect_data': correct_incorrect_data,
                       'half_half_used': request.session['half_half_used'],
                       'replacement_question_used': request.session['replacement_question_used'],
                       'disabled': [disable1, disable2]})


def replace(request):
    request.session['replacement_question_used'] = True
    replacement_question = json.loads(request.session['replacement_question'])

    correct_incorrect_layout_answers = [replacement_question['tacan_odgovor'], replacement_question['netacan1'],
                                        replacement_question['netacan2'], replacement_question['netacan3']]
    random.shuffle(correct_incorrect_layout_answers)
    request.session['correct_incorrect_layout_answers'] = correct_incorrect_layout_answers

    correct_incorrect_layout_indicators = []
    for ans in correct_incorrect_layout_answers:
        if ans == replacement_question['tacan_odgovor']:
            correct_incorrect_layout_indicators.append(1)
        else:
            correct_incorrect_layout_indicators.append(0)

    correct_incorrect_data = list(zip(correct_incorrect_layout_answers, correct_incorrect_layout_indicators))

    return render(request, "EasyQuizzy/test_singleplayer.html",
                  {'korIme': request.session['korIme'],
                   'number_current_question': request.session['number_current_question'],
                   'question_text_content': replacement_question['tekst_pitanja'],
                   'correct_incorrect_data': correct_incorrect_data,
                   'half_half_used': request.session['half_half_used'],
                   'replacement_question_used': request.session['replacement_question_used'],
                   'disabled': [4, 4]})
