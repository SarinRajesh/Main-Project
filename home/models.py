from django.contrib.auth.models import AbstractUser
from django.db import models

class UserType(models.Model):
    user_type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user_type

class Users(AbstractUser):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    user_type_id = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    home_town = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.username

class Feedback(models.Model):
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Feedback {self.id}'

class Consultation(models.Model):
    customer_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='customer_consultations')
    designer_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='designer_consultations')
    design_id = models.ForeignKey('Design', on_delete=models.CASCADE)
    date_time = models.DateTimeField(auto_now_add=True)
    consultation_status = models.CharField(max_length=100)
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, null=True, blank=True)
    proposal = models.CharField(max_length=100)

    def __str__(self):
        return f'Consultation {self.id}'

class Amount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.amount)

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)  # Updated to ForeignKey
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name

class Design(models.Model):
    designer_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='designs')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=355)
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='folio/')

    def __str__(self):
        return self.name

# ... existing code ...
class Cart(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=100, default='pending')  # Added default value
    
    def __str__(self):
        return f'Cart {self.id}'