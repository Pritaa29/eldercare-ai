from django.urls import path
from . import views
app_name = 'chatbot'
urlpatterns = [
    path('', views.chatbot_page, name='chatbot'),
    path('send/', views.send_message, name='send_message'),
    path('clear/', views.clear_chat, name='clear_chat'),
]
