from django.urls import path
from . import views

app_name = 'exercise'

urlpatterns = [
    path('', views.exercise_page, name='exercise'),
    path('analyze/', views.analyze_frame, name='analyze_frame'),
    path('advice/', views.get_ai_advice, name='get_ai_advice'),
]