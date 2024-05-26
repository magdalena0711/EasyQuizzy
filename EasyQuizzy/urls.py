from django.contrib import admin
from django.urls import path, include
from . import views_guest_and_reg, views_administrator, viewsPetar, viewsIlija, views, views_multiplayer

urlpatterns = [
    path('users', views_administrator.show_users, name='show_users'),
    path('delete', views_administrator.delete_user, name='delete_user'),
    path('addingQuestions', views_administrator.adding_questions, name='adding_questions'),
    path('addNewQuestion', views_administrator.add_new_question, name='add_new_question'),
    path('getQuestionsByCategory', views_administrator.get_questions_category, name='get_questions_by_category'),
    path('changeQuestion', views_administrator.change_question, name='change_question'),
    path('addPermittedQuestion', views_administrator.add_permitted_question, name='add_permitted_question'),
    # path('categories', views_administrator.show_categories, name='show_categories'),
    # path('addModerator', views_administrator.add_moderator, name='add_moderator'),
    path('statistics', views_guest_and_reg.statistics, name='statistics'),
    path('', views_guest_and_reg.loginUser, name='login'),
    path('dayQuestion', views_guest_and_reg.dayQuestion, name='logout'),
    path('login', views_guest_and_reg.loginUser, name='login'),
    path('loginAsGuest', views_guest_and_reg.loginAsGuest, name='loginAsGuest'),
    path('main', views_guest_and_reg.main, name='main'),
    path('questionSuggestion', views_guest_and_reg.questionSuggestion, name='questionSuggestion'),
    path('register', views_guest_and_reg.register, name='register'),
    path('logout', views_guest_and_reg.logoutUser, name='logout'),
    path('picking_choice_singleplayer_or_multiplayer', viewsPetar.doing_test_button, name='doing_test_button'),
    path('picking_category_number_of_questions_singleplayer', viewsPetar.choice_single_multi,
         name='choice_single_multi'),
    path('picking_category_number_of_questions_singleplayer_guest', viewsPetar.choice_single_multi_guest,
         name='choice_single_multi_guest'),
    path('test_singleplayer', viewsPetar.choice_category_question_number, name='choice_category_question_number'),
    path('grading_continue', viewsPetar.grading_question, name='grading_question'),
    path('test_end', viewsPetar.test_end, name='test_end'),
    path('grading_question_GET', viewsPetar.grading_question_GET, name='grading_question_GET'),
    path('test_finished_singleplayer_GET', viewsPetar.test_finished_singleplayer_GET, name='test_finished_singleplayer_GET'),
    path('choice_category_question_number_singleplayer_GET', viewsPetar.choice_category_question_number_singleplayer_GET, name='choice_category_question_number_singleplayer_GET'),
    path('categories', views_administrator.show_categories, name='show_categories'),
    path('addModerator', views_administrator.add_moderator, name='add_moderator'),
    path('permitQuestions', views_administrator.to_permit, name='questions_to_be_permitted'),
    path('addToPermitted', views_administrator.add_to_permitted, name="add_to_permitted"),
    path('addingCategories', views_administrator.changing_categories_page, name='changing_categories_page'),
    path('changeExistingCategory', views_administrator.change_existing_category, name='change_existing_category'),
    path('addQuestionForCategory', views_administrator.add_question_for_category, name='add_question_for_category'),
    path('addNewCategory', views_administrator.add_new_category, name='add_new_category'),
    path('answered', viewsIlija.answer, name='answer'),
    path('grading', viewsIlija.load_grading, name='load_grading'),
    path('fifty_fifty', viewsIlija.fifty_fifty, name='fifty_fifty'),
    path('new_question', viewsIlija.replace, name='replace'),
    path('finding/<str:room_name>/', views.find, name='find'),
    path('nextMultiplayer/<str:room_name>/', views_multiplayer.next_question, name='next_multiplayer'),
    path('jumpNext', views_multiplayer.jump_next, name="jump_next"),
    path('doneMultiplayer', views_multiplayer.done_multiplayer, name="done_multiplayer"),
    path('getCorrect', views_multiplayer.get_correct, name="get_correct"),
]