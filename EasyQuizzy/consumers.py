#Elena Savić 21/0332
#Petar Milojević 21/0336
#Ilija Miletić 21/0335
#Magdalena Obradović 21/0304

import json
import time

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django_redis import get_redis_connection
from .views_multiplayer import *
from asgiref.sync import sync_to_async
from .models import *

class Player(AsyncJsonWebsocketConsumer):

    async def connect(self):
            """
            Ulazak u lobi za čekanje drugog igrača. 
            Ova funkcija se poziva kada WebSocket pokuša da uspostavi konekciju sa serverom.
            """
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = "room_%s" % self.room_name
            
            # konektovanje na kanal za čekanje na drugog igrača preko koga se primaju poruke
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )

            await self.accept()


    async def start_game(self, event):
        """
        Javljanje svim igračima iz lobija da mogu da započnu igru.
        """
        await self.send(json.dumps(event['message']))
        

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """
        Svaki od igrača šalje poruku da je stigao u vidu svog korisničkog imena.
        Kada stigne drugi igrač on poziva funkciju koja inicijalizuje igru.
        Ta funkcija vraća redni broj trenutnog pitanja, odgovore i sva pitanja koja će učestvovati u igri.
        Povratne vrednosti se ubacuju u heš u Redis-u, koji nosi ime sobe, kako bi se koristile tokom igre.
        Svi igrači se obaveštavaju da treba da započnu igru i šalju im se korisnička imena učesnika koja su bitna za dalje prikaze.
        """
        self.username = text_data
        redis_conn = get_redis_connection("default")
        print(f'IN LOBBY {redis_conn.smembers(self.room_group_name)}')
        redis_conn.sadd(self.room_group_name, self.username)
        if (len(redis_conn.smembers(self.room_group_name)) == 2):
            # drugi korisnik koji se konektovao
            # poziv funkcije za inicijalizaciju
            current_number, correct_incorrect, questions = await sync_to_async(initialize)()
            # postavljanje rednog broja trenutnog pitanja u heš
            redis_conn.hset(self.room_name, "current_number", current_number)
            # postavljanje rečnika sa odgovorima u heš
            correct_incorrect_dict = dict()
            correct_incorrect_dict['answers'] = correct_incorrect
            redis_conn.hmset(self.room_name, {"correct_incorrect_data": json.dumps(correct_incorrect_dict)})
            # postavljanje rečnika sa pitanjima u heš
            questions_dict = dict()
            questions_dict['questions'] = questions
            redis_conn.hmset(self.room_name, {"questions": json.dumps(questions_dict)})

            # dohvatanje skupa u kome se nalaze korisnička imena svih igrača
            # korisnička imena su bitna za formiranje rečnika koji se šalje na WebSocket kako bi igrači znali protiv koga igraju
            setMembers = redis_conn.smembers(self.room_group_name)
            userNames = dict()
            keys = ['first', 'second']
            i = 0
            for mem in setMembers:
                userNames[keys[i]] = mem.decode('utf-8')
                i += 1

            # slanje obaveštenja svima koji se nalaze unutar kanala sa imenom room_group_name da započnu igru
            await self.channel_layer.group_send(self.room_group_name,
                {
                    "type": "start.game",
                    "message": userNames
                })
        elif len(redis_conn.smembers(self.room_group_name)) > 2:
            await self.send(json.dumps({'message': 'occupied'}))

    async def disconnect(self, close_code):
        """
        Napuštanje kanala za čekanje drugog igrača
        """
        # redis_conn = get_redis_connection("default")
        # redis_conn.srem(self.room_group_name, self.username)
        # print(redis_conn.smembers(self.room_group_name))

        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        
class PlayerGame(AsyncJsonWebsocketConsumer):
    async def connect(self):
            """
            Ulazak u igru.
            Ova funkcija se poziva kada WebSocket uspostavi konekciju sa stranice test_multiplayer.html.
            """
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            self.room_group_name = "quiz_%s" % self.room_name
            
            # konektovanje na kanal za igru preko koga se primaju poruke
            await self.channel_layer.group_add(
                  self.room_group_name, self.channel_name
            )

            await self.accept()

    async def both_answered(self, event):
        """
        Funkcija se poziva kada oba igrača odgovore.
        Formira se rečnik koji kao ključ koristi korisničko ime, a kao vrednost čuva listu u kojoj se nalaze odgovor, broj poena i tačan odgovor.
        Oba igrača dobijaju informacije o sebi i o onom drugom.
        """
        redis_conn = get_redis_connection("default")
        allMembers = redis_conn.hgetall(self.room_group_name)
        sending_dict = dict()
        for key, val in allMembers.items():
            val = json.loads(val)
            sending_dict[key.decode('utf-8')] = [val[0], val[1], val[2]]
    
        # slanje poruke na WebSocket
        await self.send(json.dumps(sending_dict))
    
    async def replace_question(self, event):
        """
        Ovu funkciju pozivaju oba igrača kada treba da se izvrši zamena pitanja.
        Iz skupa se uzima redni broj pitanja za zamenu i na osnovu njega se igračima šalju: novo pitanje i odgovori.
        """
        exchange_question = self.room_name + "replace"
        redis_conn = get_redis_connection("default")
        # uzimanje rednog broja pitanja za zamenu
        num = list(redis_conn.smembers(exchange_question))[0]
        num = int(num.decode('utf-8'))
        # uzimanje pitanja i odgovora na osnovu prethodno uzetog rednog broja
        questions_dict = json.loads(redis_conn.hget(self.room_name, "questions"))
        questions = questions_dict['questions']
        correct_incorrect_dict = json.loads(redis_conn.hget(self.room_name, "correct_incorrect_data"))
        correct_incorrect_list = correct_incorrect_dict['answers']
        answer_list = list()
        # formiranje liste odgovora
        for item in correct_incorrect_list[num]:
            answer_list.append(item[0])
        # formiranje rečnika koji se šalje na WebSocket
        return_dict = {'question': questions[num], 'answers': answer_list}

        #brisanje ukoliko je neko već odgovorio
        room_group_name = 'quiz_' + self.room_name
        allMembers = redis_conn.hgetall(room_group_name)
        if len(allMembers) > 0:
            for key, val in allMembers.items():
                redis_conn.hdel(room_group_name, key.decode('utf-8'))
            allMembers = redis_conn.hgetall(room_group_name)
        
        # slanje rečnika na WebSocket
        await self.send(json.dumps(return_dict))

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        """
        Ova funkcija se poziva kada stignu poruke sa WebSocket-a.
        Ukoliko stigne poruka sa odgovorima od oba igrača proverava se njihova tačnost, ažuriraju se poeni i javlja im se da su obojica odgovorili.
        Ukoliko stigne poruka o zameni pitanja ažurira se redni broj pitanja koje se koristi za zamenu i svima se javlja da je došlo do zamene.
        """
        # uspostavljanje konekcije sa Redis-om
        redis_conn = get_redis_connection("default")
        exchange_question = self.room_name + "replace"
        if text_data == "replace":
            # uzimanje rednog broja trenutnog pitanja za zamenu, uvećavanje za jedan i vraćanje u skup
            setNum = list(redis_conn.smembers(exchange_question))
            num = int(setNum[0].decode('utf-8'))
            redis_conn.srem(exchange_question, num)
            num = num + 1
            redis_conn.sadd(exchange_question, num)
            # obaveštavanje oba igrača da je došlo do zamene pitanja
            await self.channel_layer.group_send(self.room_group_name,
                        {
                            "type": "replace.question",
                            "message": 'replace'
                        })
            return

        # uzimanje rečnika u kome se nalaze: trenutno pitanje, odgovor i broj poena
        myContent =  json.loads(text_data)

        question = myContent['question']
        question = await sync_to_async(Pitanje.objects.get)(tekst_pitanja = question)
        # uzimanje tačnog odgovora na prosleđeno pitanje iz baze
        correct = question.tacan_odgovor
        # formiranje liste koja se šalje kada oba igrača odgovore
        myContentList = [myContent['answer'], myContent['points'], correct]
        
        
        print(f'LEN IN RECEIVE: {redis_conn.hlen(self.room_group_name)}')
        # ukoliko je prvi igrač odgovorio i došao drugi, vrši se provera tačnosti i ažuriranje poena
        if redis_conn.hlen(self.room_group_name) == 1:
            allMembers = redis_conn.hgetall(self.room_group_name)
            
            for key, val in allMembers.items():
                # proveravamo kako je drugi igrač odgovorio u odnosu na nas
                if key != myContent['username']:
                    val = json.loads(val)
                    answer = val[0]
                    
                    # ukoliko su oba igrača odgovorila tačno prvom se dodaju 2 poena, a drugom 1 poen
                    # ukoliko je prvi odgovorio tačno njemu se dodaju 2 poena
                    # ukoliko je drugi odgovorio tačno njemu se dodaju dva poena
                    if (answer == correct and myContent['answer'] == correct):
                        val[1] = int(val[1]) + 2
                        myContent['points'] = int(myContent['points']) + 1
                        redis_conn.hset(self.room_group_name, key, json.dumps(val))
                    elif answer == correct:
                        val[1] = int(val[1]) + 2
                        redis_conn.hset(self.room_group_name, key, json.dumps(val))
                    elif myContent['answer'] == correct:
                        myContent['points'] = int(myContent['points']) + 2

                    # obaveštavanje oba igrača da su stigli odgovori
                    await self.channel_layer.group_send(self.room_group_name,
                        {
                            "type": "both.answered",
                            "message": 'checkResults'
                        })

        # formiranje liste koja se ubacuje u heš kome pristupaju oba igrača
        # lista sadrži odgovor, broj poena i tačan odgovor; i tako za oba igrača
        # kao ključevi se koriste korisnička imena            
        myContentList = [myContent['answer'], myContent['points'], correct]
        redis_conn.hset(self.room_group_name, myContent['username'], json.dumps(myContentList))

    async def disconnect(self, close_code):
        """
        Napuštanje kanala za igru.
        Brisanje skupa u kome se nalazi redni broj pitanja za zamenu.
        Brisanje heša u kome se nalaze odgovori korisnika ukoliko je nečiji odgovor ostao.
        Ovo može da se desi ukoliko neko izađe za vreme trajanja igre.
        """
        exchange_question = self.room_name + "replace"
        redis_conn = get_redis_connection("default")
        
        setNum = list(redis_conn.smembers(exchange_question))
        if len(setNum) > 0:
            num = int(setNum[0].decode('utf-8'))
            redis_conn.srem(exchange_question, num)
        allMembers = redis_conn.hgetall(self.room_group_name)
        if len(allMembers) > 0:
            for key, val in allMembers.items():
                redis_conn.hdel(self.room_group_name, key.decode('utf-8'))
            allMembers = redis_conn.hgetall(self.room_group_name)

        lobby_group_name = "room_" + self.room_name
        room_players = redis_conn.smembers(lobby_group_name)
        for player in room_players:
            print(f'DELETED PLAYER {player}')
            redis_conn.srem(lobby_group_name, player)
            print(f'PLAYER SET {redis_conn.smembers(lobby_group_name)}')
    
        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )