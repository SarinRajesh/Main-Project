from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.models import User
from .models import Users
import random

class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp)

token_generator = CustomTokenGenerator()

def index(request):

    return render(request, 'index.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = Users.objects.get(username=username, password=password)
            return HttpResponse("Successfully Signed In")
        except Users.DoesNotExist:
            return HttpResponse("Invalid username or password.")

    return render(request, 'signin.html')

def generate_otp():
    return random.randint(100000, 999999)

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        phone = request.POST['phone']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        user_type = request.POST['user_type']

        # Store user data in session
        request.session['user_data'] = {
            'name': name,
            'phone': phone,
            'email': email,
            'username': username,
            'password': password,
            'user_type': user_type
        }
        
        otp = generate_otp()
        request.session['otp'] = otp

        # Send OTP to user's email
        send_mail(
            'Your OTP for signing in',
            f'Your OTP is {otp}',
            'your-email@gmail.com',
            [email],
            fail_silently=False,
        )

        messages.success(request, f"Check your email for the OTP.")
        
        # Redirect to verify_otp
        return redirect('verify_otp')
        
    return render(request, 'signup.html')

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        session_otp = request.session.get('otp')

        if otp == str(session_otp):
            user_data = request.session.get('user_data')
            if user_data:
                try:
                    user = Users.objects.create(
                        name=user_data['name'],
                        phone=user_data['phone'],
                        email=user_data['email'],
                        username=user_data['username'],
                        password=user_data['password'],
                        user_type=user_data['user_type']
                    )
                    user.save()
                    return redirect('signin')
                except Exception as e:
                    messages.error(request, f"Error creating account: {str(e)}")
            else:
                messages.error(request, "User data not found in session. Please sign up again.")
                return redirect('signup')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'verify_otp.html')

    return render(request, 'verify_otp.html')

def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = Users.objects.get(email=email)
            
            # Generate a password reset token and send it to the user's email
            token = token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = reverse('reset_password_confirm', kwargs={'uidb64': uidb64, 'token': token})
            reset_url = request.build_absolute_uri(reset_url)
            
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_url}',
                'your-email@gmail.com',
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset email has been sent. Check your email to proceed.')
            return redirect('request_password_reset')
        
        except Users.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('request_password_reset')

    return render(request, 'password_reset/request_password_reset.html')

def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Users.objects.get(pk=uid)
        
        if token_generator.check_token(user, token):
            # Handle password reset form submission here
            if request.method == 'POST':
                new_password = request.POST['new_password']
                confirm_password = request.POST['confirm_password']
                
                if new_password == confirm_password:
                    user.password = new_password
                    user.save()
                    messages.success(request, 'Password reset successful. You can now sign in with your new password.')
                    return redirect('signin')
                else:
                    messages.error(request, 'Passwords do not match. Please try again.')
                    return render(request, 'password_reset/reset_password_confirm.html', {'uidb64': uidb64, 'token': token})
            
            return render(request, 'password_reset/reset_password_confirm.html', {'uidb64': uidb64, 'token': token})
        
        else:
            messages.error(request, 'Invalid password reset link.')
            return redirect('signin')
    
    except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None
    
    return redirect('signin')
