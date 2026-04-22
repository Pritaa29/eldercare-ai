from django.urls import path
from . import views

app_name = 'carecentre'

urlpatterns = [
    path('', views.carecentre_page, name='carecentre'),
    path('search/', views.search_nearby, name='search_nearby'),
    path('details/<str:place_id>/', views.get_place_details, name='place_details'),
]