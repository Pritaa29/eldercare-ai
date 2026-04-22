from django.db import models

class MedicineProfile(models.Model):
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=100, default='Patient')
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Medicine(models.Model):
    FREQUENCY_CHOICES = [('once','Once a day'),('twice','Twice a day'),('thrice','Three times a day'),('four','Four times a day'),('custom','Custom')]
    MEAL_CHOICES = [('before','Before meal'),('after','After meal'),('with','With meal'),('anytime','Anytime')]
    profile = models.ForeignKey(MedicineProfile, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='once')
    meal_timing = models.CharField(max_length=10, choices=MEAL_CHOICES, default='after')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['name']

class ReminderTime(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='reminder_times')
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['time']
