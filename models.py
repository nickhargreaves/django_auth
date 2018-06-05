from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=40, null=True, blank=True)
    key_expires = models.DateTimeField(null=True, blank=True)
    phone_number = models.CharField(max_length=40, null=True, blank=True)
    sms_activation = models.CharField(max_length=40, null=True, blank=True)
