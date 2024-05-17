# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/easyquizzy/finding/(?P<room_name>\w+)/$", consumers.Player.as_asgi()),
]