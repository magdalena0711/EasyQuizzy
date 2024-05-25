# chat/routing.py
from django.urls import re_path

from .consumers import *

websocket_urlpatterns = [
    re_path(r"ws/easyquizzy/finding/(?P<room_name>\w+)/$", Player.as_asgi()),
    re_path(r"ws/easyquizzy/nextMultiplayer/(?P<room_name>\w+)/$", PlayerGame.as_asgi())
]