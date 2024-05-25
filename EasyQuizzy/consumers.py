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
            print('connected')
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            print(self.room_name)
            self.room_group_name = "quiz_%s" % self.room_name
            print(self.room_group_name)
            #print(self.channel_name)
            # Join room group
            await self.channel_layer.group_add(
                  self.room_group_name, self.channel_name
            )



            await self.accept()






    async def start_game(self, event):
        await self.send(json.dumps(event['message']))
        #print(event['message'])

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        print(text_data)
        self.username = text_data
        redis_conn = get_redis_connection("default")
        redis_conn.sadd(self.room_group_name, self.username)
        if (len(redis_conn.smembers(self.room_group_name)) == 2):
            # drugi korisnik koji se konektovao
            #print('poslao')
            current_number, correct_incorrect, questions = await sync_to_async(initialize)()
            redis_conn.hset(self.room_name, "current_number", current_number)
            correct_incorrect_dict = dict()
            correct_incorrect_dict['answers'] = correct_incorrect

            redis_conn.hmset(self.room_name, {"correct_incorrect_data": json.dumps(correct_incorrect_dict)})
            # print(redis_conn.hget("data", "correct_incorrect_data"))
            questions_dict = dict()
            questions_dict['questions'] = questions
            redis_conn.hmset(self.room_name, {"questions": json.dumps(questions_dict)})

            setMembers = redis_conn.smembers(self.room_group_name)
            userNames = dict()
            keys = ['first', 'second']
            i = 0
            for mem in setMembers:
                userNames[keys[i]] = mem.decode('utf-8')
                i += 1

            await self.channel_layer.group_send(self.room_group_name,
                {
                    "type": "start.game",
                    "message": userNames
                })

        

    async def disconnect(self, close_code):
        # Leave room group
        redis_conn = get_redis_connection("default")
        redis_conn.srem(self.room_group_name, self.username)

        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        
class PlayerGame(AsyncJsonWebsocketConsumer):
    async def connect(self):
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            #print(self.room_name)
            self.room_group_name = "quiz_%s" % self.room_name
            #print(self.channel_name)
            # Join room group
            await self.channel_layer.group_add(
                  self.room_group_name, self.channel_name
            )


            await self.accept()


            # if(len(redis_conn.smembers(self.room_group_name)) == 2):
            #     pass

    async def both_answered(self, event):
        redis_conn = get_redis_connection("default")
        allMembers = redis_conn.hgetall(self.room_group_name)
        sending_dict = dict()
        #print(allMembers)
        for key, val in allMembers.items():
            val = json.loads(val)
            print(f'KEY {key} VAL {val}')
            sending_dict[key.decode('utf-8')] = [val[0], val[1], val[2]]

        #print(redis_conn.hlen(self.room_group_name))
    
        await self.send(json.dumps(sending_dict))
        

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        redis_conn = get_redis_connection("default")
        #print(text_data)
        
        myContent =  json.loads(text_data)
        print(myContent)
        #timeMillis = round(time.time() * 1000)
        

        question = myContent['question']
        question = await sync_to_async(Pitanje.objects.get)(tekst_pitanja = question)
        #print(question)
        correct = question.tacan_odgovor
        #print(correct)
        myContentList = [myContent['answer'], myContent['points'], correct]
        
        #print(self.room_group_name)
        print(f'LEN IN RECEIVE: {redis_conn.hlen(self.room_group_name)}')
        if redis_conn.hlen(self.room_group_name) == 1:
            allMembers = redis_conn.hgetall(self.room_group_name)
            #print(allMembers)
            
            for key, val in allMembers.items():
                if key != myContent['username']:
                    val = json.loads(val)
                    answer = val[0]
                    
                    if (answer == correct and myContent['answer'] == correct):
                        val[1] = int(val[1]) + 2
                        myContent['points'] = int(myContent['points']) + 1
                        #print('prvo')
                        redis_conn.hset(self.room_group_name, key, json.dumps(val))
                    elif answer == correct:
                        val[1] = int(val[1]) + 2
                        #print('drugo')
                        redis_conn.hset(self.room_group_name, key, json.dumps(val))
                    elif myContent['answer'] == correct:
                        #print('trece')
                        myContent['points'] = int(myContent['points']) + 2
                    await self.channel_layer.group_send(self.room_group_name,
                        {
                            "type": "both.answered",
                            "message": 'checkResults'
                        })

        #print(myContent)            
        myContentList = [myContent['answer'], myContent['points'], correct]
        redis_conn.hset(self.room_group_name, myContent['username'], json.dumps(myContentList))


        

    async def disconnect(self, close_code):
        # Leave room group
        redis_conn = get_redis_connection("default")
        redis_conn.srem(self.room_group_name, self.channel_name)

        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )