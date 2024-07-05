from django.db import IntegrityError



from ..models import Message, PrivateChat, Usuario
from asgiref.sync import  sync_to_async, async_to_sync
from channels.db import database_sync_to_async
@sync_to_async
def  message_to_dict(message: Message):
    from ..serializers import MessageSerializer
    
    return  MessageSerializer(message).data

def user_to_dict(user: Usuario):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'roles': user.get_roles()
    }

@sync_to_async
def add_message(identifier, sender, destination, content):
    if not (identifier and sender  and content):
        raise ValueError("identifier, sender, and content cannot be None")
    
    chat, _ = PrivateChat.objects.get_or_create(identifier=identifier)
    
    message = Message.objects.create(
        chat=chat,
        sender=sender,
        content= content
    )

    chat.chat_users.add(sender)
    chat.chat_users.add(destination)
    
    # if not created:
    #     message.content = content

    message.save()
    
    chat.save()
    
    return message



@sync_to_async
def get_messages(identifier):
    chat = PrivateChat.objects.prefetch_related('messages').get(identifier=identifier)
    return list(chat.messages.select_related('sender').order_by('timestamp'))

@database_sync_to_async
def add_private_chat(identifier):
    chat, _ = PrivateChat.objects.get_or_create(identifier=identifier)
    return chat
  