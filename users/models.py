from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    role = models.CharField(max_length=20, default="user")
    blocked = models.BooleanField(default=False) 
