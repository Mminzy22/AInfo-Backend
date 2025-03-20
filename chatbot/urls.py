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
        "room/<int:pk>/",
        ChatRoomDetailDeleteUpdateView.as_view(),
        name="chatroom-detail-delete-patch",
    ),
    path("room/<int:pk>/logs/", ChatLogListView.as_view(), name="chatlog-list"),
]
