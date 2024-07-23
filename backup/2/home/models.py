from django.db import models

class Users_table(models.Model):
    USER_TYPE_CHOICES = [
        ('designer', 'Designer'),
        ('customer', 'Customer'),
    ]

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.username
