from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    status = models.CharField(max_length=20, default='active')  # Added status field
    deactivation_reason = models.TextField(blank=True, null=True)  # New field for reason

    def __str__(self):
        return self.username

class Feedback(models.Model):
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Feedback {self.id}'


class Payment_Type(models.Model):
    payment_type = models.CharField(max_length=100, unique=True, default=0)

    def __str__(self):
        return self.payment_type

class Amount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.amount)
        
class Consultation(models.Model):
    customer_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='customer_consultations')
    designer_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='designer_consultations')
    design_id = models.ForeignKey('Design', on_delete=models.CASCADE)
    date_time = models.DateTimeField()  # Change this to DateTimeField without auto_now_add
    consultation_status = models.CharField(max_length=100)
    feedback = models.ForeignKey(Feedback, on_delete=models.SET_NULL, null=True, blank=True)
    proposal = models.CharField(max_length=100)
    schedule_date_time = models.DateTimeField(null=True, blank=True)
    room_length = models.DecimalField(max_digits=5, decimal_places=2)
    room_width = models.DecimalField(max_digits=5, decimal_places=2)
    room_height = models.DecimalField(max_digits=5, decimal_places=2)
    design_preferences = models.TextField(blank=True, null=True)
    payment_type = models.ForeignKey(Payment_Type, on_delete=models.CASCADE,default=0)
    payment_status = models.CharField(max_length=100, default='pending')
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f'Consultation {self.id}'


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)  # Changed to CharField
    image = models.ImageField(upload_to='product_images/')
    stock = models.PositiveIntegerField(default=0)  
    color = models.CharField(max_length=7, null=True, blank=True)

    def __str__(self):
        return self.name

class Design(models.Model):
    designer_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='designs')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=355)
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='folio/')
    category = models.CharField(max_length=100)  # New category field with default value
    sqft = models.DecimalField(max_digits=10, decimal_places=2,default=0)  # Added sqft field with default value

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


class Order(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, limit_choices_to={'user_type_id__user_type': 'Customer'})
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False)
    amount = models.ForeignKey(Amount, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=100)
    payment_type = models.ForeignKey(Payment_Type, on_delete=models.CASCADE,default=0)
    payment_status = models.CharField(max_length=100)
    delivery_date = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f'Order {self.id}'
    

class ConsultationDate(models.Model):
    designer = models.ForeignKey(Users, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        # Update this line to remove 'design' from unique_together
        unique_together = ('designer', 'date_time')

    def __str__(self):
        return f"{self.designer.username} - {self.date_time}"
    
from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    sender = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username if self.receiver else 'Unknown'}: {self.content[:50]}"
    


from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
    
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MoodBoard(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='mood_boards/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MoodBoardItem(models.Model):
    ITEM_TYPE_CHOICES = (
        ('design', 'Design'),
        ('product', 'Product'),
    )
    mood_board = models.ForeignKey(MoodBoard, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    design = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)

    def __str__(self):
        return f"Item for {self.mood_board.name}"

    @property
    def image_url(self):
        if self.item_type == 'design' and self.design:
            return self.design.image.url
        elif self.item_type == 'product' and self.product:
            return self.product.image.url
        return ''

    @property
    def caption(self):
        if self.item_type == 'design' and self.design:
            return self.design.name
        elif self.item_type == 'product' and self.product:
            return self.product.name
        return ''