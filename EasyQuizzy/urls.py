from django.contrib import admin
from django.urls import path, include
from . import views_guest_and_reg, views_administrator

urlpatterns = [

    path('users', views_administrator.show_users, name='show_users'),
    path('delete', views_administrator.delete_user, name='delete_user'),
    path('addingQuestions', views_administrator.adding_questions, name='adding_questions'),
    path('addNewQuestion', views_administrator.add_new_question, name='add_new_question'),
    path('getQuestionsByCategory', views_administrator.get_questions_category, name='get_questions_by_category'),
    path('changeQuestion', views_administrator.change_question, name='change_question'),
    path('addPermittedQuestion', views_administrator.add_permitted_question, name='add_permitted_question'),
    path('categories', views_administrator.show_categories, name='show_categories'),
    path('addModerator', views_administrator.add_moderator, name='add_moderator'),
    path('statistics', views_guest_and_reg.statistics, name='statistics'),
    #path('bestRatedQuestions/', views_guest_and_reg.bestRatedQuestions, name='bestRatedQuestions'),
    path('', views_guest_and_reg.login, name='login'),
    path('login', views_guest_and_reg.login, name='login'),
    path('main', views_guest_and_reg.main, name='main'),
    path('questionSuggestion', views_guest_and_reg.questionSuggestion, name='questionSuggestion'),
    path('register', views_guest_and_reg.register, name='register'),
    path('logout', views_guest_and_reg.logout, name='logout'),
    path('permitQuestions', views_administrator.to_permit, name='questions_to_be_permitted'),
    path('addToPermitted', views_administrator.add_to_permitted, name="add_to_permitted")
]