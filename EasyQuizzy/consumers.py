import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class Player(AsyncJsonWebsocketConsumer):

      async def connect(self):
            print('connected')
            self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
            print(self.room_name)
            self.room_group_name = "chat_%s" % self.room_name

            # Join room group
            self.channel_layer.group_add(
                  self.room_group_name, self.channel_name
            )
            await self.accept()


      async def receive(self, text_data=None, bytes_data=None, **kwargs):
            if text_data == 'PING':
                await self.send('PONG')

      async def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        
