from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    path('', views.emergency_page, name='emergency'),
    path('sos/', views.trigger_sos, name='trigger_sos'),
    path('contact/add/', views.add_contact, name='add_contact'),
    path('contact/delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
]