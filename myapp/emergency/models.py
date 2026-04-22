# """Emergency alert system models."""

# from django.db import models


# class EmergencyContact(models.Model):
#     session_id = models.CharField(max_length=100, db_index=True)
#     name = models.CharField(max_length=100)
#     relationship = models.CharField(max_length=50, default='Family Member')
#     email = models.EmailField(blank=True)
#     telegram_chat_id = models.CharField(max_length=50, blank=True,
#         help_text='Telegram chat ID for instant alerts')
#     phone = models.CharField(max_length=20, blank=True)
#     is_primary = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} ({self.relationship})"

#     class Meta:
#         ordering = ['-is_primary', 'name']


# class EmergencyAlert(models.Model):
#     STATUS_CHOICES = [('sent', 'Sent'), ('failed', 'Failed'), ('pending', 'Pending')]

#     session_id = models.CharField(max_length=100, db_index=True)
#     patient_name = models.CharField(max_length=100, default='Patient')
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)
#     address = models.TextField(blank=True)
#     message = models.TextField(blank=True)
#     contacts_notified = models.IntegerField(default=0)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Alert {self.id} — {self.status} at {self.created_at}"

#     class Meta:
#         ordering = ['-created_at']



"""Emergency alert system models."""

from django.db import models


class EmergencyContact(models.Model):
    session_id = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, default='Family Member')
    email = models.EmailField(blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True,
        help_text='Telegram chat ID for instant alerts')
    phone = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"

    class Meta:
        ordering = ['-is_primary', 'name']


class EmergencyAlert(models.Model):
    STATUS_CHOICES = [('sent', 'Sent'), ('failed', 'Failed'), ('pending', 'Pending')]

    session_id = models.CharField(max_length=100, db_index=True)
    patient_name = models.CharField(max_length=100, default='Patient')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(blank=True)
    message = models.TextField(blank=True)
    contacts_notified = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert {self.id} — {self.status} at {self.created_at}"

    class Meta:
        ordering = ['-created_at']