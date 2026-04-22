from django.urls import path
from . import views

app_name = 'signlanguage'

urlpatterns = [
    path('', views.signlanguage_page, name='signlanguage'),
    path('analyze/', views.analyze_sign, name='analyze_sign'),
    path('upload/', views.analyze_uploaded_sign, name='analyze_uploaded'),
]