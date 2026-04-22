# import os
# from celery import Celery

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elderycare.settings')

# app = Celery('elderycare')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()


"""ElderCare AI — Celery"""
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eldercare.settings')
app = Celery('eldercare')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()