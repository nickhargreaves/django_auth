from django.db import models
from django.contrib.auth.models import User


# Create a user model

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    phone_number = models.CharField(max_length=40, default="000")
    sms_activation = models.CharField(max_length=40, default="000")
    username = models.CharField(max_length=40, default="000")
