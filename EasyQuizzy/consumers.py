import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django_redis import get_redis_connection
from .views_multiplayer import *
from asgiref.sync import sync_to_async

class Player(AsyncJsonWebsocketConsumer):

    async def connect(self):
            print('connected')
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            print(self.room_name)
            self.room_group_name = "quiz_%s" % self.room_name
            #print(self.channel_name)
            # Join room group
            await self.channel_layer.group_add(
                  self.room_group_name, self.channel_name
            )

            redis_conn = get_redis_connection("default")
            redis_conn.sadd(self.room_group_name, self.channel_name)

            print(len(redis_conn.smembers(self.room_group_name)))
            print(redis_conn.smembers(self.room_group_name))

            await self.accept()


            if(len(redis_conn.smembers(self.room_group_name)) == 2):
                #drugi korisnik koji se konektovao
                print('poslao')
                current_number, correct_incorrect, questions = await sync_to_async(initialize)()
                redis_conn.hset("data", "current_number", current_number)
                correct_incorrect_dict = dict()
                correct_incorrect_dict['answers'] = correct_incorrect

                redis_conn.hmset("data", {"correct_incorrect_data": json.dumps(correct_incorrect_dict)})
                #print(redis_conn.hget("data", "correct_incorrect_data"))
                questions_dict = dict()
                questions_dict['questions'] = questions
                redis_conn.hmset("data", {"questions": json.dumps(questions_dict)})

                await self.channel_layer.group_send(self.room_group_name,
                {
                    "type" : "start.game",
                    "message" : "START"
                })



    async def start_game(self, event):
        await self.send("START")
        print(event['message'])

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        print(text_data)

    async def disconnect(self, close_code):
        # Leave room group
        redis_conn = get_redis_connection("default")
        redis_conn.srem(self.room_group_name, self.channel_name)

        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        
class PlayerGame(AsyncJsonWebsocketConsumer):
    async def connect(self):
            print('connected')
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            print(self.room_name)
            self.room_group_name = "quiz_%s" % self.room_name
            #print(self.channel_name)
            # Join room group
            await self.channel_layer.group_add(
                  self.room_group_name, self.channel_name
            )

            redis_conn = get_redis_connection("default")
            redis_conn.sadd(self.room_group_name, self.channel_name)

            print(len(redis_conn.smembers(self.room_group_name)))
            print(redis_conn.smembers(self.room_group_name))

            await self.accept()


            if(len(redis_conn.smembers(self.room_group_name)) == 2):
                pass



    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        print(text_data)

    async def disconnect(self, close_code):
        # Leave room group
        redis_conn = get_redis_connection("default")
        redis_conn.srem(self.room_group_name, self.channel_name)

        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )