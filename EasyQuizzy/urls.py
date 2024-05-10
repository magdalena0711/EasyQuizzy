from django.contrib import admin
from django.urls import path, include
from EasyQuizzy import views, views_administrator

urlpatterns = [
    path('', views.statistics, name='statistics'),
    path('users', views_administrator.show_users, name='show_users'),
    path('delete', views_administrator.delete_user, name='delete_user'),
    path('addingQuestions', views_administrator.adding_questions, name='adding_questions'),
    path('addNewQuestion', views_administrator.add_new_question, name='add_new_question'),
    path('getQuestionsByCategory', views_administrator.get_questions_category, name='get_questions_by_category'),
    path('changeQuestion', views_administrator.change_question, name='change_question'),
    path('addPermittedQuestion', views_administrator.add_permitted_question, name='add_permitted_question'),
    path('categories', views_administrator.show_categories, name='show_categories'),
    path('addModerator', views_administrator.add_moderator, name='add_moderator')
]