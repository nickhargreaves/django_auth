from django.db import models
from django.contrib.auth.models import User


# Create a user model

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
