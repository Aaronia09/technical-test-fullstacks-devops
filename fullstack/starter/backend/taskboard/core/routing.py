from django.urls import re_path
from tasks.consumers import TasksConsumer

websocket_urlpatterns = [
    re_path(r"ws/tasks/?$", TasksConsumer.as_asgi()),
]
