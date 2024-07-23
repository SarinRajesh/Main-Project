from django.contrib.auth.models import AbstractUser
from django.db import models

class Users(AbstractUser):
    USER_TYPE_CHOICES = [
        ('designer', 'Designer'),
        ('customer', 'Customer'),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    address = models.TextField(null=True, blank=True)  # Allow null values
    home_town = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return self.username
