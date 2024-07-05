import hashlib
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
import jwt
   
class CompanyConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        

        if self.user.is_anonymous:
            await self.close()


        self.room_group_name = f'group_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.channel_layer.group_send(
            self.room_group_name, { 
                  'type': 'user_joined',
                  'user': self.user,
            }
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name, { 
                  'type': 'user_disconnect',
                  'user': self.user,
            }
        )


    async def receive(self, text_data):
        
        text_data_json = json.loads(text_data)

        message = text_data_json['message']
        token = text_data_json['token']

        # _type = text_data_json['type']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'group_message',
                'message': message,
                'user': {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email,
                    'token': token,
                    'roles': self.user.get_roles()

                }
            }
        )
        

    async def group_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_joined",
            "user": 
                 {
                    'id': event["user"].id,
                    'username': event["user"].username,
                    'roles': self.user.get_roles()

                },
            "message": f"{event["user"].username} se ha unido al chat",
        }))

    async def user_disconnect(self, event):
        await self.send(text_data=json.dumps({
            "type": "user_disconnect",
            "user": 
                 {
                    'id': event["user"].id,
                    'username': event["user"].username,
                    'roles': self.user.get_roles()

                },
            "message": f"{event["user"].username} se ha desconectado al chat",
        }))
