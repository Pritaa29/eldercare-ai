from celery import shared_task
@shared_task
def check_medicine_reminders():
    pass  # Browser-side notifications handle reminders; this is a stub
