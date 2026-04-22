from django.urls import path
from . import views

app_name = 'medicine'

urlpatterns = [
    path('', views.medicine_page, name='medicine'),
    path('add/', views.add_medicine, name='add_medicine'),
    path('delete/<int:medicine_id>/', views.delete_medicine, name='delete_medicine'),
    path('acknowledge/', views.acknowledge_reminder, name='acknowledge'),
    path('api/list/', views.get_medicines_api, name='api_list'),
    path('api/due/', views.get_due_reminders, name='api_due'),  # NEW: for polling
]
