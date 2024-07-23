# home/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import Users_table

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data
        name = data.get('name')
        phone = data.get('phone')
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type', 'customer')  # Default to customer if not provided

        Users_table.objects.create(
            name=name,
            phone=phone,
            email=user.email,
            username=username,
            password=password,  # Ensure this is hashed if you're storing it this way
            user_type=user_type
        )
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        if not user.pk:
            user.save()
        
        Users_table.objects.get_or_create(
            email=user.email,
            defaults={
                'name': user.get_full_name(),
                'phone': '',  # Google login may not provide phone, set default
                'username': user.username,
                'password': '',  # Password is managed by Google, so set as blank
                'user_type': 'customer',  # Default to customer
            }
        )
        return user
