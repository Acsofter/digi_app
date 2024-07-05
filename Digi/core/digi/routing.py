from django.urls import re_path
from .consumers.company import CompanyConsumer

websocket_urlpatterns = [
    re_path(r'ws/company/(?P<room_name>\w+)/$', CompanyConsumer.as_asgi()),
    # re_path(r'ws/pm/(?P<user_name>\w+)/$', PMConsumer.as_asgi()),
]
