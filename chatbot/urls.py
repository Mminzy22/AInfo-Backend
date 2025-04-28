from django.urls import path

from .views import (
    ChatLogListView,
    ChatRoomDetailDeleteUpdateView,
    ChatRoomListCreateView,
)

app_name = "chatbot"
urlpatterns = [
    path("room/", ChatRoomListCreateView.as_view(), name="chatroom-list-create"),
    path(
        "room/<uuid:pk>/",
        ChatRoomDetailDeleteUpdateView.as_view(),
        name="chatroom-detail-delete-patch",
    ),
    path("room/<uuid:pk>/logs/", ChatLogListView.as_view(), name="chatlog-list"),
]
