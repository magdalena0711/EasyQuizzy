from django.test import TestCase,Client
from django.urls import reverse
from EasyQuizzy.models import Kategorija
import base64
import math
from django.db import connection

from django.contrib.auth import get_user_model
class TestViews(TestCase):

    def test_play(self):

        response = self.client.get(reverse('doing_test_button'))
        print(response)

        self.assertEquals(200,response.status_code)
        self.assertTemplateUsed(response,'EasyQuizzy/picking_choice_singleplayer_or_multiplayer.html')

    def setUp(self):

        sql_file_path = 'tests/popunjenaBaza.sql'

        # Open and read the SQL file
        with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as sql_file:
            sql_statements = sql_file.read()

        # Execute SQL statements to create tables and insert data
        with connection.cursor() as cursor:
            cursor.execute(sql_statements)
        
        client=Client()
        self.client=client
        self.username='igrac123'
        self.password='Psii123+'
        self.user=get_user_model().objects.create_user(username=self.username,password=self.password)

        categories = ['Opste znanje', 'Muzika', 'Umetnost', 'Knjizevnost', 'Kinematografija', 'Sport', 'Istorija', 'Geografija', 'Desavanja u svetu', 'Igrice']
        img_path = ['EasyQuizzy/static/css/collage3.jpg']

        with open(img_path[0], 'rb') as img:
            img_bytes = img.read()
        self.category = Kategorija.objects.create(naziv = categories[0], slika= img_bytes)
    
    # def test_picking_singleplayer(self):
    #     response = self.client.get(reverse('choice_single_multi'))
        
    #     # images=[]  
    #     # for cat in categories:
    #     #     images.append(base64.b64encode(cat.slika).decode())

    #     # length_range = math.ceil((len(categories)-4)/5)
    #     # list_images=[]
    #     # for cat in categories:
    #     #     list_images.append((cat.idkat//5)-1)

    #     # data = list(zip(categories,images,list_images))

    #     keys = ["data", "range"]
    #     for key in keys:
    #         self.assertIn(key, response.context)
    #     self.assertEquals(response.context['data'], self.category)
    #     # self.assertEquals(response.context['range'], range(length_range))
        
    #     self.assertEquals(200,response.status_code)
    #     self.assertTemplateUsed(response,'EasyQuizzy/picking_category_number_of_questions_singleplayer.html')


    # def test_film(self):
    #     client=Client()
    #     response=client.get(reverse('film',args=[self.film.id]))
    #     print(response)
    #     self.assertEquals(response.status_code,200)
    #     self.assertEquals(response.context['film'].id,self.film.id)


    # def test_if_aut(self):

    #     self.client.login(username=self.username,password=self.password)
    #     response=self.client.get(reverse('login'))
    #     self.assertRedirects(response,reverse('home'))



    # def test_login_f(self):
    #     response=self.client.post(reverse('login'),{"username":'neki',"password":'drugi'})
    #     self.assertEquals(response.status_code,200)
    #     self.assertTemplateUsed(response,'filmovi/login.html')

    # def test_login_t(self):
    #     response=self.client.post(reverse('login'),{'username':'Kristijan','password':'Ziza'},follow=True)
    #     self.assertRedirects(response,reverse('home'))
