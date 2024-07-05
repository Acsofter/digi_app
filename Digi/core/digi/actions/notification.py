from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer


@sync_to_async
def send_notification_to_user(sender_destination, user_destination, message):
    channel_layer = get_channel_layer()
    sync_to_async(channel_layer.group_send)( f"notification_{user_destination.username}", {
            'type': 'user_notification',
            'message':
                {
                    'type': 'new_message',
                    'user': sender_destination.username,
                    'message': message
                }
            
        })