from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password
from .models import UserType, Consultation, Users, Design, Amount, Product, Cart, Review, Order, Payment_Type, ConsultationDate
from .decorators import nocache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from allauth.socialaccount.models import SocialAccount
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import random
from django.utils.dateparse import parse_datetime, parse_date
from decimal import Decimal, InvalidOperation
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.middleware.csrf import get_token
from django.db.models import Sum
from django.db import transaction
from django.core.exceptions import ValidationError
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import json
import re
from datetime import datetime, time
from django.views.decorators.cache import never_cache


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp)

token_generator = CustomTokenGenerator()

@nocache
def index(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user
        user_type = user.user_type_id.user_type if user.user_type_id else None
        context = {'user': user, 'user_type': user_type}
    return render(request, 'index.html', context)


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.status == 'active':  # Check if user is active
                login(request, user)  # Log in the user
                return custom_login_redirect(request)  # Redirect to the appropriate page
            else:
                # Store message in session under a custom key
                request.session['custom_error_message'] = "User account is inactive."
                return redirect('signin')  # Redirect to sign-in page
        else:
            # Store message in session under a custom key
            request.session['custom_error_message'] = "Invalid username or password."
            return redirect('signin')  # Redirect to sign-in page
    
    return render(request, 'signin.html')


def custom_login_redirect(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('signin')

    if user.status != 'active':  # Check if user is active
        logout(request)  # Log out inactive users
        # Store message in session under a custom key
        request.session['custom_error_message'] = "User account is inactive."
        return redirect('signin')  # Redirect to sign-in page

    if user.user_type_id and user.user_type_id.user_type == 'Admin':
        return redirect('admin_index')
    else:
        return redirect('index')



def generate_otp():
    return random.randint(100000, 999999)

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.user_type_id = UserType.objects.get(user_type='Customer')
        if commit:
            user.save()
        return user

# Update the CustomSocialAccountAdapter class
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Check if the email already exists in the database
        email = sociallogin.account.extra_data['email']
        if email:
            try:
                user = Users.objects.get(email=email)
                # If the user exists, connect the social account to the existing user
                sociallogin.connect(request, user)
            except Users.DoesNotExist:
                pass  # If the user doesn't exist, proceed with the normal flow

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.user_type_id = UserType.objects.get(user_type='Customer')
        user.save()
        return user

# Update the signup function
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if a user with this email already exists
        existing_user = Users.objects.filter(email=email).first()
        if existing_user:
            # If the user exists, check if they have a social account
            social_account = SocialAccount.objects.filter(user=existing_user).first()
            if social_account:
                messages.error(request, "An account with this email already exists. Please use Google login.")
                return redirect('signin')

        # Store user data in session
        request.session['user_data'] = {
            'name': name,
            'phone': phone,
            'email': email,
            'username': username,
            'password': password,
        }
        
        otp = generate_otp()
        request.session['otp'] = otp

        # Send OTP to user's email
        send_mail(
            'Your OTP for signing up',
            f'Your OTP is {otp}',
            'your-email@gmail.com',  # Replace with your actual email
            [email],
            fail_silently=False,
        )

        messages.success(request, "Check your email for the OTP.")
        return redirect('verify_otp')
        
    return render(request, 'signup.html')

# Update the verify_otp function
def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if otp == str(session_otp):
            user_data = request.session.get('user_data')
            if user_data:
                try:
                    # Check if a user with this email already exists
                    existing_user = Users.objects.filter(email=user_data['email']).first()
                    if existing_user:
                        # If the user exists, update their information
                        existing_user.name = user_data['name']
                        existing_user.phone = user_data['phone']
                        existing_user.username = user_data['username']
                        existing_user.password = make_password(user_data['password'])
                        existing_user.save()
                        user = existing_user
                    else:
                        # Create a new user with the provided data
                        user = Users.objects.create(
                            name=user_data['name'],
                            phone=user_data['phone'],
                            email=user_data['email'],
                            username=user_data['username'],
                            password=make_password(user_data['password']),
                            user_type_id=UserType.objects.get(user_type='Customer')
                        )

                    # Log the user in
                    backend = 'django.contrib.auth.backends.ModelBackend'
                    user = authenticate(username=user_data['username'], password=user_data['password'], backend=backend)
                    if user is not None:
                        login(request, user)
                    
                    # Clear user data from session
                    request.session.pop('user_data', None)

                    return redirect('index')
                except Exception as e:
                    messages.error(request, f"Error creating account: {str(e)}")
            else:
                messages.error(request, "User data not found in session. Please sign up again.")
                return redirect('signup')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')


def check_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': Users.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

def check_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': Users.objects.filter(username=username).exists()
    }
    return JsonResponse(data)

def request_password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
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
                'your-email@gmail.com',  # Replace with your actual email
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
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                
                if new_password == confirm_password:
                    user.password = make_password(new_password)  # Hash the password
                    user.save()
                    messages.success(request, 'Password reset successful. You can now sign in with your new password.')
                    return redirect('signin')
                else:
                    messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'password_reset/reset_password_confirm.html', {'uidb64': uidb64, 'token': token})
        else:
            messages.error(request, 'Invalid password reset link.')
            return redirect('signin')
    
    except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None
    
    return redirect('signin')

def logout_view(request):
    logout(request)
    return redirect('signin')



@nocache
@login_required
def profile(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    return render(request, 'profile.html', {'user': user, 'user_type': user_type})

@login_required
def edit_profile(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None

    if request.method == 'POST':
        # Update user profile fields
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        user.home_town = request.POST.get('home_town')
        user.district = request.POST.get('district')
        user.state = request.POST.get('state')
        user.pincode = request.POST.get('pincode')

        # Handle photo upload if present
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']

        try:
            user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return redirect('edit_profile')

    context = {
        'user': user,
        'user_type': user_type
    }
    return render(request, 'edit_profile.html', context)



@login_required
@csrf_exempt
def upload_photo(request):
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            user = request.user
            user.photo = photo
            user.save()
            return JsonResponse({'success': True, 'photo_url': user.photo.url})
    return JsonResponse({'success': False})



@login_required
@nocache
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        amount_value = request.POST.get('amount')
        image = request.FILES.get('image')
        category = request.POST.get('category')
        stock = request.POST.get('stock')
        color = request.POST.get('color')  # Add this line to get the color value

        amount = Amount(amount=amount_value)
        amount.save()

        product = Product(
            name=name,
            description=description,
            amount=amount,
            category=category,
            image=image,
            stock=stock,
            color=color  # Add this line to save the color
        )
        product.save()

        return redirect('add_product')

    return render(request, 'admin_page/add_product.html')

@login_required
@nocache
def add_portfolio(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None

    # Check if user details are complete
    user_details_complete = all([
        user.name,
        user.email,
        user.phone,
        user.address,
        user.home_town,
        user.district,
        user.state,
        user.pincode
    ])

    if request.method == 'POST':
        if not user_details_complete:
            messages.error(request, 'Please complete your profile before adding a portfolio.')
            return redirect('profile')

        name = request.POST.get('name')
        description = request.POST.get('description')
        amount_value = request.POST.get('amount')
        image = request.FILES.get('image')
        category = request.POST.get('category')
        sqft = request.POST.get('sqft', 0)

        amount = Amount(amount=amount_value)
        amount.save()

        portfolio = Design(
            designer_id=request.user,
            name=name,
            description=description,
            amount=amount,
            image=image,
            category=category,
            sqft=sqft
        )
        portfolio.save()

        messages.success(request, 'Portfolio added successfully.')
        return redirect('portfolio')

    context = {
        'user_type': user_type,
        'user_details_complete': user_details_complete
    }
    return render(request, 'add_portfolio.html', context)


from django.http import JsonResponse
from django.template.loader import render_to_string

@nocache
def portfolio(request):
    category = request.GET.get('category', 'all')
    sqft_range = request.GET.get('sqft_range', 'all')

    if request.user.is_authenticated and request.user.user_type_id.user_type == 'Designer':
        # For designers, show only their designs
        portfolios = Design.objects.filter(designer_id=request.user)
    else:
        # For other users, show all designs
        portfolios = Design.objects.all()
        designer = request.GET.get('designer', 'all')
        if designer != 'all':
            portfolios = portfolios.filter(designer_id__username=designer)

    if category != 'all':
        portfolios = portfolios.filter(category__iexact=category)

    if sqft_range != 'all':
        if sqft_range == '0-500':
            portfolios = portfolios.filter(sqft__lte=500)
        elif sqft_range == '501-1000':
            portfolios = portfolios.filter(sqft__gt=500, sqft__lte=1000)
        elif sqft_range == '1001-1500':
            portfolios = portfolios.filter(sqft__gt=1000, sqft__lte=1500)
        elif sqft_range == '1501+':
            portfolios = portfolios.filter(sqft__gt=1500)

    all_designers = Users.objects.filter(user_type_id__user_type='Designer').values_list('username', flat=True).distinct()
    
    # Fetch all unique categories from the Design model
    all_categories = Design.objects.values_list('category', flat=True).distinct()

    # Format categories
    def format_category(category):
        return category.replace('_', ' ').title()

    formatted_categories = [{'value': cat, 'display': format_category(cat)} for cat in all_categories]

    context = {
        'portfolios': portfolios,
        'designers': all_designers,
        'categories': formatted_categories,
        'no_results': portfolios.count() == 0,
        'selected_category': category,
        'selected_sqft_range': sqft_range,
    }

    if request.user.is_authenticated:
        user = request.user
        user_type = user.user_type_id.user_type if user.user_type_id else None
        context['user_type'] = user_type

    return render(request, 'portfolio.html', context)

@login_required
def delete_portfolio(request, portfolio_id):
    # Get the design item or return 404 if not found
    design = get_object_or_404(Design, id=portfolio_id)
    
    # Check if the current user is the owner of the design item
    if request.user == design.designer_id:
        # Delete the design item
        design.delete()
        messages.success(request, "Portfolio item deleted successfully.")
    else:
        messages.error(request, "You don't have permission to delete this portfolio item.")
    
    # Redirect to the portfolio list page or wherever you want
    return redirect('portfolio')  # Make sure 'portfolio' is the correct name for your portfolio list view

@nocache
def shop(request):
    products = Product.objects.all()
    
    # Get filter parameters
    category = request.GET.get('category')
    price_order = request.GET.get('price_order')
    
    # Filter by category
    if category and category != 'all':
        products = products.filter(category=category)
    
    # Order by price
    if price_order == 'low_to_high':
        products = products.order_by('amount__amount')
    elif price_order == 'high_to_low':
        products = products.order_by('-amount__amount')
    
    # Get unique categories for the dropdown
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'selected_price_order': price_order,
    }

    if request.user.is_authenticated:
        user = request.user
        user_type = user.user_type_id.user_type if user.user_type_id else None
        context['user_type'] = user_type
        context['user'] = user

        # Get cart items for the current user
        cart_items = Cart.objects.filter(user_id=user)
        context['cart_items'] = cart_items
        context['cart_total'] = sum(item.amount for item in cart_items)
        context['cart_count'] = cart_items.count()

    return render(request, 'shop.html', context)

from django.shortcuts import render, get_object_or_404


@login_required
@nocache
def portfolio_details(request, portfolio_id):
    portfolio = get_object_or_404(Design.objects.select_related('designer_id'), id=portfolio_id)
    
    # Replace underscores with spaces in the category
    portfolio.category_display = portfolio.category.replace("_", " ")
    
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None

    # Check if user details are complete
    user_details_complete = all([
        user.address,
        user.home_town,
        user.district,
        user.state,
        user.pincode
    ])

    if request.method == 'POST':
        # Check if the request is to reject a consultation
        if 'reject' in request.POST:
            consultation = Consultation.objects.filter(
                design_id=portfolio_id,
                customer_id=user,
                designer_id=portfolio.designer_id
            ).first()

            if consultation:
                # Find the corresponding ConsultationDate and set is_booked to False
                ConsultationDate.objects.filter(
                    designer=portfolio.designer_id,
                    date_time=consultation.schedule_date_time
                ).update(is_booked=False)

                # Delete the consultation entry
                consultation.delete()

                messages.success(request, 'Consultation request cancelled.')
            else:
                messages.error(request, 'Consultation not found.')

            return redirect('portfolio_details', portfolio_id=portfolio_id)

    # Check for existing consultation status
    consultation_status = Consultation.objects.filter(
        design_id=portfolio_id,
        customer_id=user,
        designer_id=portfolio.designer_id
    ).values_list('consultation_status', flat=True).first()
    
    context = {
        'portfolio': portfolio,
        'user_type': user_type,
        'consultation_status': consultation_status,
        'user_details_complete': user_details_complete,
        'is_designer': user == portfolio.designer_id,
    }
    return render(request, 'portfolio_details.html', context)
logout_view
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import ChatMessage, Design, Users


@login_required
@require_POST
def send_chat_message(request):
    data = json.loads(request.body)
    content = data.get('content')
    design_id = data.get('design_id')

    if content and design_id:
        design = Design.objects.get(id=design_id)
        sender = request.user
        
        # Determine the receiver based on the sender's user type
        if sender == design.designer_id:
            # If the sender is the designer, find the customer who initiated the consultation
            consultation = Consultation.objects.filter(design_id=design, designer_id=sender).first()
            receiver = consultation.customer_id if consultation else None
        else:
            # If the sender is not the designer (i.e., a customer), set the receiver to the designer
            receiver = design.designer_id

        message = ChatMessage.objects.create(
            sender=sender,
            receiver=receiver,
            design=design,
            content=content
        )
        return JsonResponse({'status': 'success', 'message_id': message.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid data'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from .models import Design, ChatMessage, Users
import json

@login_required
def get_chat_messages(request):
    design_id = request.GET.get('design_id')
    last_message_id = request.GET.get('last_message_id')
    
    if design_id:
        design = Design.objects.get(id=design_id)
        
        # Get messages newer than the last_message_id
        messages = ChatMessage.objects.filter(design=design, id__gt=last_message_id).order_by('timestamp')
        
        # Mark messages as read if the user is the receiver
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        messages_data = [
            {
                'id': message.id,
                'sender_username': message.sender.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'is_sender': message.sender == request.user,
                'is_designer': message.sender == design.designer_id
            }
            for message in messages
        ]
        return JsonResponse({
            'status': 'success', 
            'messages': messages_data,
            'designer_username': design.designer_id.username,
            'current_user': request.user.username
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid design_id'})


@login_required
@csrf_exempt
def consultation_booking(request, portfolio_id):
    portfolio = get_object_or_404(Design.objects.select_related('designer_id', 'amount'), id=portfolio_id)
    
    # Fetch available consultation dates for the designer
    available_dates = ConsultationDate.objects.filter(
        designer=portfolio.designer_id,
        date_time__gte=timezone.now(),
        is_booked=False
    ).order_by('date_time')

    if request.method == 'POST':
        schedule_date = request.POST.get('schedule_date')
        room_length = Decimal(request.POST.get('room_length', '0'))
        room_width = Decimal(request.POST.get('room_width', '0'))
        room_height = Decimal(request.POST.get('room_height', '0'))
        design_preferences = request.POST.get('design_preferences')

        # Create or get the Amount instance
        consultation_amount = Amount.objects.create(amount=Decimal('500.00'))  # 500 INR as the consultation fee

        # Parse the schedule_date
        try:
            schedule_date = parse_date(schedule_date)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

        if not schedule_date:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'})

        # Find the ConsultationDate object for the selected date
        consultation_date = ConsultationDate.objects.filter(
            designer=portfolio.designer_id,
            date_time__date=schedule_date,
            is_booked=False
        ).first()

        if not consultation_date:
            return JsonResponse({'status': 'error', 'message': 'Selected date is not available'})

        # Create consultation object
        consultation = Consultation(
            customer_id=request.user,
            designer_id=portfolio.designer_id,
            design_id=portfolio,
            date_time=consultation_date.date_time,
            consultation_status='Requested',
            proposal='Pending',
            schedule_date_time=consultation_date.date_time,
            room_length=room_length,
            room_width=room_width,
            room_height=room_height,
            design_preferences=design_preferences,
            payment_type=Payment_Type.objects.get(payment_type='online'),
            payment_status='Paid',
            amount=consultation_amount
        )
        consultation.save()

        # Mark the selected date as booked
        consultation_date.is_booked = True
        consultation_date.save()

        return JsonResponse({'status': 'success', 'message': 'Consultation booked successfully'})
    
    context = {
        'portfolio': portfolio,
        'user_type': request.user.user_type_id.user_type if request.user.user_type_id else None,
        'available_dates': available_dates,
    }
    return render(request, 'consultation_booking.html', context)

from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta

@nocache
def product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:3]
    
    # Calculate delivery date (7 days from today)
    delivery_date = timezone.now().date() + timedelta(days=7)
    
    # Format the delivery date
    formatted_delivery_date = delivery_date.strftime("%A, %B %d, %Y")
    
    if request.method == 'POST' and request.user.is_authenticated:
        review_content = request.POST.get('review')
        rating = request.POST.get('rating')  # Add this line to get the rating
        if review_content and rating:
            Review.objects.create(
                product=product,
                user=request.user,
                content=review_content,
                rating=int(rating)  # Add this line to save the rating
            )
            messages.success(request, "Your review has been posted successfully.")
            return redirect('product', product_id=product.id)
        else:
            messages.error(request, "Review content and rating cannot be empty.")
    
    # Fetch reviews and count after potential new review creation
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    review_count = reviews.count()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_count': review_count,
        'avg_rating': round(avg_rating, 1),  # Round to 1 decimal place
        'product_amount_paise': int(product.amount.amount * 100),  # Convert to paise
        'csrf_token': get_token(request),  # Add CSRF token to context
        'delivery_date': formatted_delivery_date,  # Add this line
    }

    print(f"Debug - Delivery Date: {formatted_delivery_date}")  # Add this debug print

    if request.user.is_authenticated:
        user = request.user
        user_type = user.user_type_id.user_type if user.user_type_id else None
        context['user_type'] = user_type
        context['user'] = user

        # Get cart items for the current user
        cart_items = Cart.objects.filter(user_id=user).select_related('product_id__amount')
        context['cart_items'] = cart_items
        context['cart_total'] = cart_items.aggregate(total=Sum('amount'))['total'] or 0
        context['cart_count'] = cart_items.count()

        if request.method == 'POST':
            if 'product_id' in request.POST:
                product_id = int(request.POST.get('product_id'))
                status = request.POST.get('status')
                quantity = int(request.POST.get('quantity', 1))
                amount_value = request.POST.get('amount')
                
                if status == 'Added':
                    product_instance = get_object_or_404(Product, id=product_id)
                    
                    try:
                        unit_price = Decimal(amount_value)
                    except (InvalidOperation, TypeError):
                        unit_price = product_instance.amount.amount

                    cart_item, created = Cart.objects.get_or_create(
                        user_id=user,
                        product_id=product_instance,
                        defaults={'quantity': quantity, 'amount': unit_price * quantity, 'status': status}
                    )
                    
                    if not created:
                        cart_item.quantity += quantity
                        cart_item.amount = unit_price * cart_item.quantity
                        cart_item.save()

                    messages.success(request, 'Product added to cart successfully.')
                    return redirect('product', product_id=product_id)

    # Get related products (same category, excluding the current product)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    context['related_products'] = related_products

    # Get and clear the cart message from the session
    cart_message = messages.get_messages(request)
    context['cart_message'] = cart_message

    return render(request, 'product.html', context)



@login_required
@never_cache
def cart(request):
    cart_items = Cart.objects.filter(user_id=request.user)
    
    # Calculate total price
    total_price = sum(item.amount for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

@login_required
@never_cache
@require_POST
@csrf_protect
def update_cart_quantity(request):
    import json
    from decimal import Decimal
    data = json.loads(request.body)
    item_id = data.get('item_id')
    quantity = int(data.get('quantity'))

    try:
        cart_item = get_object_or_404(Cart, id=item_id, user_id=request.user)
        
        # Calculate unit price if `amount` was previously calculated as total amount
        unit_price = cart_item.amount / cart_item.quantity
        cart_item.quantity = quantity
        cart_item.amount = unit_price * quantity
        
        # Save the updated cart item
        cart_item.save()

        # Recalculate total price for the updated cart
        cart_items = Cart.objects.filter(user_id=request.user)
        total_price = sum(item.amount for item in cart_items)

        return JsonResponse({
            'success': True,
            'total_price': float(total_price),
            'item_total': float(cart_item.amount),
            'total_items': sum(item.quantity for item in cart_items)
        })
    except Cart.DoesNotExist:
        return JsonResponse({'success': False}, status=400)

@login_required
@never_cache
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user_id=request.user.id)
    cart_item.delete()
    
    # Recalculate total price and items count
    cart_items = Cart.objects.filter(user_id=request.user)
    total_price = sum(item.amount for item in cart_items)
    total_items = sum(item.quantity for item in cart_items)
    
    return JsonResponse({
        'success': True,
        'total_price': float(total_price),
        'total_items': total_items
    })
@login_required
@require_POST
def clear_cart(request):
    Cart.objects.filter(user_id=request.user).delete()
    return JsonResponse({'status': 'success'})


@login_required
@require_POST
def create_order_from_product(request):
    try:
        with transaction.atomic():
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            product = Product.objects.get(id=product_id)
            
            # Check if there's enough stock
            if product.stock < quantity:
                return JsonResponse({'status': 'error', 'message': f'Not enough stock for {product.name}'}, status=400)
            
            # Create or get the Amount instance
            amount_value = product.amount.amount * quantity
            amount, _ = Amount.objects.get_or_create(amount=amount_value)
            
            # Get or create the Payment_Type instance
            payment_type, _ = Payment_Type.objects.get_or_create(payment_type='online')
            
            # Create the order
            order = Order.objects.create(
                user=request.user,
                product=product,
                quantity=quantity,
                amount=amount,
                order_date=timezone.now(),
                order_status='Pending',
                delivery_date=timezone.now() + timedelta(days=7),
                payment_type=payment_type,
                payment_status='Paid'
            )
            
            # Update product stock
            product.stock -= quantity
            product.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Order created successfully.',
                'order_id': order.id
            })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

import logging

logger = logging.getLogger(__name__)

@login_required
@require_POST
def create_order_from_cart(request):
    try:
        with transaction.atomic():
            cart_items = Cart.objects.filter(user_id=request.user)
            
            if not cart_items.exists():
                return JsonResponse({'status': 'error', 'message': 'Your cart is empty'}, status=400)
            
            orders_created = []
            
            for cart_item in cart_items:
                product = cart_item.product_id
                quantity = cart_item.quantity
                
                # Check if there's enough stock
                if product.stock < quantity:
                    if quantity == 1:
                        return JsonResponse({'status': 'error', 'message': f'Not enough stock for {product.name}, only {product.stock} available.'}, status=400)
                    else:
                        continue  # Skip this item if quantity is greater than available stock
                
                # Create or get the Amount instance
                amount_value = product.amount.amount * quantity
                amount, _ = Amount.objects.get_or_create(amount=amount_value)
                
                # Get or create the Payment_Type instance
                payment_type, _ = Payment_Type.objects.get_or_create(payment_type='online')
                
                # Create the order
                order = Order.objects.create(
                    user=request.user,
                    product=product,
                    quantity=quantity,
                    amount=amount,
                    order_date=timezone.now(),
                    order_status='Pending',
                    delivery_date=timezone.now() + timedelta(days=7),
                    payment_type=payment_type,
                    payment_status='Paid'
                )
                
                orders_created.append(order)
                
                # Update product stock
                product.stock -= quantity
                product.save()
                
                # Remove item from cart
                cart_item.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Successfully created {len(orders_created)} orders.',
                'order_ids': [order.id for order in orders_created]
            })
    except Exception as e:
        logger.error(f"Error processing order: {e}")  # Log the error for debugging
        return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your order. Please try again later.'}, status=500)

@nocache
@login_required
def orders(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    
    # Fetch orders for the current user
    orders = Order.objects.filter(user=user).select_related('product', 'amount').order_by('-order_date')
    
    context = {
        'orders': orders,
        'user_type': user_type,
        'user': user
    }
    return render(request, 'my_orders.html', context)



@login_required
@require_http_methods(["GET", "POST"])
def schedule_consultation(request):
    if request.method == 'POST':
        date_time_str = request.POST.get('date_time')
        date_time = parse_datetime(date_time_str)

        if not date_time:
            return JsonResponse({'status': 'error', 'message': 'Invalid date-time format'})

        # Make the datetime timezone-aware
        date_time = timezone.make_aware(date_time, timezone.get_current_timezone())

        if date_time < timezone.now():
            return JsonResponse({'status': 'error', 'message': 'Cannot schedule consultations for past dates'})

        consultation_date, created = ConsultationDate.objects.get_or_create(
            designer=request.user,
            date_time=date_time,
            defaults={'is_booked': False}
        )

        if created:
            return JsonResponse({'status': 'success', 'message': 'Consultation date scheduled successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'This date and time is already scheduled'})

    else:
        # Handle GET request
        consultation_dates = ConsultationDate.objects.filter(designer=request.user).values('date_time', 'is_booked')
        consultation_dates_list = [
            {
                'id': date['date_time'].isoformat(),
                'title': 'Consultation',
                'start': date['date_time'].isoformat(),
                'allDay': False,
                'className': 'past-date' if date['date_time'] < timezone.now() else '',
                'editable': date['date_time'] >= timezone.now() and not date['is_booked']
            } for date in consultation_dates
        ]
        
        context = {
            'consultation_dates': json.dumps(consultation_dates_list)
        }
        return render(request, 'schedule_consultation.html', context)



@login_required
@require_POST
def remove_scheduled_date(request):
    date_time_str = request.POST.get('date_time')
    try:
        date_time = parse_datetime(date_time_str)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid date-time format'})

    if not date_time:
        return JsonResponse({'status': 'error', 'message': 'Invalid date-time format'})

    consultation_date = get_object_or_404(ConsultationDate, designer=request.user, date_time=date_time)

    if consultation_date.is_booked:
        return JsonResponse({'status': 'error', 'message': 'Cannot remove a booked consultation date'})

    consultation_date.delete()
    return JsonResponse({'status': 'success', 'message': 'Consultation date removed successfully'})


@nocache
@login_required
@require_POST
def edit_portfolio(request, portfolio_id):
    # Ensure the user is a designer and owns this portfolio
    portfolio = get_object_or_404(Design, id=portfolio_id, designer_id=request.user)
    
    if request.user.user_type_id.user_type != 'Designer':
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    name = request.POST.get('name')
    description = request.POST.get('description')
    image = request.FILES.get('image')
    amount_value = request.POST.get('amount')
    category = request.POST.get('category')  # New: Get the category from the POST request
    sqft = request.POST.get('sqft')  # New: Get the sqft from the POST request

    try:
        portfolio.name = name
        portfolio.description = description
        
        if image:
            portfolio.image = image
        
        if amount_value:
            # Update or create the amount
            if portfolio.amount:
                portfolio.amount.amount = amount_value
                portfolio.amount.save()
            else:
                amount = Amount.objects.create(amount=amount_value)
                portfolio.amount = amount

        if category:  # New: Update the category if provided
            portfolio.category = category

        if sqft:  # New: Update the sqft if provided
            portfolio.sqft = sqft

        portfolio.save()

        return redirect('portfolio_details', portfolio_id=portfolio_id)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

@nocache
@login_required
def consultations(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    designer = Users.objects.get(username=user.username)
    consultations = Consultation.objects.filter(designer_id=designer).select_related('customer_id', 'design_id')
    
    if request.method == 'POST':
        if 'consultation_id' in request.POST:
            consultation_id = request.POST.get('consultation_id')
            action = request.POST.get('action')
            
            consultation = Consultation.objects.get(id=consultation_id)
            
            if action == 'approve':
                consultation.consultation_status = 'Approved'
                consultation.save()
            elif action == 'cancel':
                consultation.delete()
            
            return redirect('consultations')
    
    context = {
        'consultations': consultations,
        'user_type': user_type,
    }
    return render(request, 'consultations.html', context)

@nocache
@login_required
def my_consultations(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    
    # Fetch consultations for the current user
    consultations = Consultation.objects.filter(customer_id=user).select_related('designer_id', 'design_id')
    
    context = {
        'consultations': consultations,
        'user_type': user_type,
    }
    return render(request, 'my_consultations.html', context)



@login_required
def add_designer(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate username existence
        if Users.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'admin_page/add_designer.html')
        
        # Validate email existence
        if Users.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'admin_page/add_designer.html')

        # Validate password criteria
        password_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        if not password_pattern.match(password):
            messages.error(request, 'Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, one number, and one special character.')
            return render(request, 'admin_page/add_designer.html')
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'admin_page/add_designer.html')
        
        try:
            designer_type = UserType.objects.get(user_type='Designer')
            
            new_designer = Users.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                user_type_id=designer_type
            )
            new_designer.save()
            
            # Send email with username and password
            send_mail(
                'Welcome to ElegantDecor',
                f'Dear {username},\n\nYour account has been successfully created. Your login credentials are as follows:\nUsername: {username}\nPassword: {password}\n\nBest regards,\nThe ElegantDecor Team',
                'your-email@gmail.com',  # Replace with your actual email
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Designer added successfully.')
            return redirect('tables')
        except Exception as e:
            messages.error(request, f'Error adding designer: {str(e)}')
    
    return render(request, 'admin_page/add_designer.html')



@nocache
@login_required
def users_table(request):
    customers = Users.objects.filter(user_type_id__user_type='Customer')
    designers = Users.objects.filter(user_type_id__user_type='Designer')

    if 'download' in request.GET:
        user_type = request.GET.get('user_type', '')
        if user_type not in ['customer', 'designer']:
            return HttpResponse('Invalid user type')

        if request.GET['download'] == 'pdf':
            return download_pdf(request, 'users', user_type)
        elif request.GET['download'] == 'excel':
            return download_excel(request, 'users', user_type)

    return render(request, 'admin_page/users_table.html', {
        'customers': customers,
        'designers': designers,
    })

@nocache
@login_required
def designs_table(request):
    designs = Design.objects.select_related('designer_id', 'amount').all()
    
    if 'download' in request.GET:
        if request.GET['download'] == 'pdf':
            return download_pdf(request, 'designs')
        elif request.GET['download'] == 'excel':
            return download_excel(request, 'designs')
    
    context = {
        'designs': designs,
    }
    return render(request, 'admin_page/designs_table.html', context)


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from openpyxl import Workbook
from io import BytesIO

def download_pdf(request, data_type, user_type=None):
    template_path = 'admin_page/table_pdf_template.html'
    
    if data_type == 'users':
        if user_type == 'customer':
            filename = 'customers_table.pdf'
            title = 'Customers'
            users = Users.objects.filter(user_type_id__user_type='Customer')
        elif user_type == 'designer':
            filename = 'designers_table.pdf'
            title = 'Designers'
            users = Users.objects.filter(user_type_id__user_type='Designer')
        else:  # all users
            filename = 'all_users_table.pdf'
            title = 'All Users'
            users = Users.objects.exclude(user_type_id__user_type='Admin')

        headers = ['Name', 'Email', 'Phone', 'Address', 'Home Town', 'District', 'State', 'Pincode', 'Status', 'User Type']
        items = [
            [
                user.name,
                user.email,
                user.phone,
                user.address,
                user.home_town,
                user.district,
                user.state,
                user.pincode,
                user.status,
                user.user_type_id.user_type if user.user_type_id else 'N/A'
            ] for user in users
        ]
    elif data_type == 'designs':
        filename = 'designs_table.pdf'
        title = 'Designs'
        headers = ['Name', 'Description', 'Designer', 'Amount', 'Category', 'Square Feet']
        designs = Design.objects.select_related('designer_id', 'amount').all()
        items = [
            [
                design.name,
                design.description[:50] + ('...' if len(design.description) > 50 else ''),
                design.designer_id.name,
                str(design.amount.amount),
                design.category,
                str(design.sqft)
            ] for design in designs
        ]
    elif data_type == 'consultations':
        filename = 'consultations_table.pdf'
        title = 'Consultations'
        headers = ['Customer', 'Designer', 'Design', 'Status', 'Scheduled Date', 'Payment Type', 'Payment Status', 'Amount']
        consultations = Consultation.objects.select_related('customer_id', 'designer_id', 'design_id', 'payment_type', 'amount').all()
        items = [
            [
                consultation.customer_id.name,
                consultation.designer_id.name,
                consultation.design_id.name,
                consultation.consultation_status,
                str(consultation.schedule_date_time),
                consultation.payment_type.payment_type,
                consultation.payment_status,
                str(consultation.amount.amount)
            ] for consultation in consultations
        ]
    elif data_type == 'products':
        filename = 'products_table.pdf'
        title = 'Products'
        headers = ['Name', 'Description', 'Amount', 'Stock', 'Category']
        products = Product.objects.select_related('amount').all()
        items = [
            [
                product.name,
                product.description[:50] + ('...' if len(product.description) > 50 else ''),
                str(product.amount.amount),
                str(product.stock),
                product.category
            ] for product in products
        ]
    elif data_type == 'orders':
        filename = 'orders_table.pdf'
        title = 'Orders'
        headers = ['Order ID', 'User', 'Product', 'Quantity', 'Amount', 'Order Date', 'Order Status', 'Payment Type', 'Payment Status']
        orders = Order.objects.select_related('user', 'product', 'amount', 'payment_type').all()
        items = [
            [
                str(order.id),
                order.user.username,
                order.product.name,
                str(order.quantity),
                str(order.amount.amount),
                order.order_date.strftime('%Y-%m-%d %H:%M'),
                order.order_status,
                order.payment_type.payment_type,
                order.payment_status
            ] for order in orders
        ]
    elif data_type == 'products':
        filename = 'products_table.pdf'
        title = 'Products'
        headers = ['Name', 'Description', 'Amount', 'Stock', 'Category']
        products = Product.objects.select_related('amount').all()
        items = [
            [
                product.name,
                product.description[:50] + ('...' if len(product.description) > 50 else ''),
                str(product.amount.amount),
                str(product.stock),
                product.category
            ] for product in products
        ]
    else:
        return HttpResponse('Invalid data type')

    context = {
        'title': title,
        'headers': headers,
        'items': items,
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def download_excel(request, data_type, user_type=None):
    workbook = Workbook()
    worksheet = workbook.active

    if data_type == 'users':
        if user_type == 'customer':
            worksheet.title = 'Customers'
            filename = 'customers_table.xlsx'
            data = Users.objects.filter(user_type_id__user_type='Customer')
        else:  # designer
            worksheet.title = 'Designers'
            filename = 'designers_table.xlsx'
            data = Users.objects.filter(user_type_id__user_type='Designer')

        headers = ['Name', 'Email', 'Phone', 'Address', 'Home Town', 'District', 'State', 'Pincode', 'Status']
    elif data_type == 'designs':
        worksheet.title = 'Designs'
        headers = ['Name', 'Description', 'Designer', 'Amount', 'Category', 'Square Feet']
        data = Design.objects.select_related('designer_id', 'amount').all()
        filename = 'designs_table.xlsx'
    elif data_type == 'consultations':
        worksheet.title = 'Consultations'
        headers = ['Customer', 'Designer', 'Design', 'Status', 'Scheduled Date', 'Payment Type', 'Payment Status', 'Amount']
        data = Consultation.objects.select_related('customer_id', 'designer_id', 'design_id').all()
        filename = 'consultations_table.xlsx'
    elif data_type == 'products':
        filename = 'products_table.xlsx'
        worksheet.title = 'Products'
        headers = ['Name', 'Description', 'Amount', 'Stock', 'Category']
        worksheet.append(headers)
        
        products = Product.objects.select_related('amount').all()
        for product in products:
            worksheet.append([
                product.name,
                product.description[:50] + ('...' if len(product.description) > 50 else ''),
                str(product.amount.amount),
                str(product.stock),
                product.category
            ])
        
        # Create a BytesIO buffer for the Excel file
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Create the HttpResponse object with Excel mime type
        response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
    elif data_type == 'orders':
        filename = 'orders_table.xlsx'
        worksheet.title = 'Orders'
        headers = ['Order ID', 'User', 'Product', 'Quantity', 'Amount', 'Order Date', 'Order Status', 'Payment Type', 'Payment Status']
        worksheet.append(headers)
        
        orders = Order.objects.select_related('user', 'product', 'amount', 'payment_type').all()
        for order in orders:
            worksheet.append([
                str(order.id),
                order.user.username,
                order.product.name,
                str(order.quantity),
                str(order.amount.amount),
                order.order_date.strftime('%Y-%m-%d %H:%M'),
                order.order_status,
                order.payment_type.payment_type,
                order.payment_status
            ])
        
        # Create a BytesIO buffer for the Excel file
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        # Create the HttpResponse object with Excel mime type
        response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
    else:
        return HttpResponse('Invalid data type')

    # Add headers
    for col_num, header in enumerate(headers, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = header

    # Add data
    for row_num, item in enumerate(data, 2):
        if data_type == 'users':
            row = [
                item.name,
                item.email,
                item.phone,
                item.address,
                item.home_town,
                item.district,
                item.state,
                item.pincode,
                item.status,
            ]
        elif data_type == 'designs':
            row = [
                item.name,
                item.description[:50] + '...' if len(item.description) > 50 else item.description,
                item.designer_id.name,
                str(item.amount.amount),
                item.category,
                str(item.sqft)
            ]
        elif data_type == 'consultations':
            row = [
                item.customer_id.name,
                item.designer_id.name,
                item.design_id.name,
                item.consultation_status,
                str(item.schedule_date_time),
                item.payment_type.payment_type,
                item.payment_status,
                str(item.amount.amount)
            ]
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    # Create a BytesIO buffer for the Excel file
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Create the HttpResponse object with Excel mime type
    response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    return response

    
@nocache
@login_required
def consultations_table(request):
    consultations = Consultation.objects.select_related('customer_id', 'designer_id', 'design_id').all()
    
    if 'download' in request.GET:
        if request.GET['download'] == 'pdf':
            return download_pdf(request, 'consultations')
        elif request.GET['download'] == 'excel':
            return download_excel(request, 'consultations')
    
    context = {
        'consultations': consultations
    }
    return render(request, 'admin_page/consultations_table.html', context)

@nocache
@login_required
def orders_table(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        
        order = get_object_or_404(Order, id=order_id)
        if action == 'approve':
            order.order_status = 'Completed'
            message = f'Order #{order_id} has been approved and marked as completed.'
        elif action == 'cancel':
            order.order_status = 'Cancelled'
            message = f'Order #{order_id} has been cancelled.'
        
        order.save()
        messages.success(request, message)
        return redirect('orders_table')

    if 'download' in request.GET:
        if request.GET['download'] == 'pdf':
            return download_pdf(request, 'orders')
        elif request.GET['download'] == 'excel':
            return download_excel(request, 'orders')

    orders = Order.objects.all().select_related('user', 'product', 'amount', 'payment_type').order_by('-order_date')
    context = {
        'orders': orders
    }
    return render(request, 'admin_page/orders_table.html', context)
@nocache
@login_required
@require_http_methods(["GET", "POST"])
def products_table(request):
    if request.method == 'POST':
        if '_method' in request.POST and request.POST['_method'] == 'DELETE':
            # Handle product delete
            product_id = request.POST.get('id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            return JsonResponse({'status': 'success'})
        
        # Handle product update
        product_id = request.POST.get('id')
        product = get_object_or_404(Product, id=product_id)
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.amount.amount = request.POST.get('amount')
        product.stock = request.POST.get('stock')
        product.category = request.POST.get('category')  # Make sure this line is present
        product.color = request.POST.get('color')
        product.save()
        product.amount.save()
        return JsonResponse({'status': 'success'})

    # For GET requests, handle downloads and render the table
    if 'download' in request.GET:
        if request.GET['download'] == 'pdf':
            return download_pdf(request, 'products')
        elif request.GET['download'] == 'excel':
            return download_excel(request, 'products')

    # For GET requests, render the table
    products = Product.objects.select_related('amount').all()
    context = {
        'products': products
    }
    return render(request, 'admin_page/products_table.html', context)

@nocache
@login_required
def admin_index(request):
    
    return render(request, 'admin_page/admin_index.html')


from django.utils import timezone
from datetime import timedelta

@nocache
@login_required
def orders(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    
    # Fetch orders for the current user
    orders = Order.objects.filter(user=user).select_related(
        'product', 'amount', 'payment_type', 'user'
    ).order_by('-order_date')
    
    # Calculate and add delivery date for each order
    for order in orders:
        order.delivery_date = order.order_date + timedelta(days=7)
    
    context = {
        'orders': orders,
        'user_type': user_type,
        'user': user
    }
    return render(request, 'my_orders.html', context)


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

@login_required
def download_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.order_status != 'Completed':
        messages.error(request, "Receipt is only available for completed orders.")
        return redirect('my_orders')

    # Render the receipt HTML
    template = get_template('receipt.html')
    context = {'order': order}
    html = template.render(context)

    # Create a PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    
    if not pdf.err:
        # Generate response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_order_{order.id}.pdf"'
        response.write(result.getvalue())
        return response

    return HttpResponse('Error generating PDF', status=400)



@login_required
@require_POST
def remove_scheduled_date(request):
    date_time_str = request.POST.get('date_time')
    try:
        date_time = parse_datetime(date_time_str)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid date-time format'})

    if not date_time:
        return JsonResponse({'status': 'error', 'message': 'Invalid date-time format'})

    consultation_date = get_object_or_404(ConsultationDate, designer=request.user, date_time=date_time)

    if consultation_date.is_booked:
        return JsonResponse({'status': 'error', 'message': 'Cannot remove a booked consultation date'})

    consultation_date.delete()
    return JsonResponse({'status': 'success', 'message': 'Consultation date removed successfully'})

import cv2
import numpy as np
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.conf import settings
from django.db.models import Q
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier

# Load the dataset and train the KNN model
data = pd.read_csv(os.path.join(settings.BASE_DIR, 'data/colors.csv'))
X = data[['R', 'G', 'B']]
y = data['ColorName1']  # Use ColorName1 for the color names
knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X, y)

def detect_color(image_path):
    # Check if the file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The file {image_path} does not exist.")

    # Load the image using OpenCV
    image = cv2.imread(image_path)
    
    # Check if the image is loaded properly
    if image is None:
        raise ValueError(f"Failed to load image from {image_path}. The file may not be a valid image format.")
    
    # Resize image for faster processing
    image = cv2.resize(image, (300, 300))
    # Convert image from BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Reshape image to be a list of pixels
    pixels = np.float32(image.reshape(-1, 3))

    # Use k-means clustering to find the dominant color
    n_colors = 1
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert the dominant color to a tuple
    dominant_color = palette[0].astype(int)
    
    # Predict the closest color using the KNN model
    detected_color = knn.predict([dominant_color])[0]
    return detected_color

def recommend_products_by_color(request):
    context = {}
    if request.user.is_authenticated:
        user_type = request.user.user_type_id.user_type if request.user.user_type_id else None
        context['user_type'] = user_type

    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']
        
        # Save the file and get the path
        file_name = default_storage.save(f'uploads/{image.name}', ContentFile(image.read()))
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"The file {file_path} does not exist after saving.")
            
            detected_color = detect_color(file_path)
            
            # Remove underscore and capitalize each word
            formatted_color = detected_color.replace('_', ' ').title()
            
            # Filter products based on the detected color
            color_query = Q(color__iexact=detected_color)
            recommended_products = Product.objects.filter(color_query)
            
            context.update({
                'detected_color': formatted_color,  # Use the formatted color name
                'recommended_products': recommended_products,
                'products_count': recommended_products.count(),
                'form_submitted': True,
                'image_url': default_storage.url(file_name)
            })
        except Exception as e:
            context.update({
                'error': str(e),
                'form_submitted': True
            })
    else:
        context['form_submitted'] = False
    
    return render(request, 'recommend_products.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import MoodBoard, MoodBoardItem
@nocache
@login_required
def mood_board_list(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None

    mood_boards = MoodBoard.objects.filter(user=user)

    context = {
        'mood_boards': mood_boards,
        'user_type': user_type,
        'user': user,
        'no_results': mood_boards.count() == 0,
    }

    return render(request, 'mood_boards/list.html', context)

@login_required
def create_mood_board(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        MoodBoard.objects.create(user=user, name=name, description=description, image=image)
        return redirect('mood_board_list')
    return render(request, 'mood_boards/create.html', {'user_type': user_type})

@login_required
def mood_board_detail(request, pk):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    mood_board = get_object_or_404(MoodBoard, pk=pk, user=user)
    items = mood_board.items.all()
    return render(request, 'mood_boards/detail.html', {'mood_board': mood_board, 'items': items, 'user_type': user_type})

@login_required
def add_design_to_mood_board(request, pk):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    mood_board = get_object_or_404(MoodBoard, pk=pk, user=user)
    
    # Get filter parameters
    category = request.GET.get('category', 'all')
    designer = request.GET.get('designer', 'all')
    sqft_range = request.GET.get('sqft_range', 'all')

    designs = Design.objects.all()

    if category != 'all':
        designs = designs.filter(category__iexact=category)

    if designer != 'all':
        designs = designs.filter(designer_id__username=designer)

    if sqft_range != 'all':
        if sqft_range == '0-500':
            designs = designs.filter(sqft__lte=500)
        elif sqft_range == '501-1000':
            designs = designs.filter(sqft__gt=500, sqft__lte=1000)
        elif sqft_range == '1001-1500':
            designs = designs.filter(sqft__gt=1000, sqft__lte=1500)
        elif sqft_range == '1501+':
            designs = designs.filter(sqft__gt=1500)

    all_designers = Users.objects.filter(user_type_id__user_type='Designer').values_list('username', flat=True).distinct()
    all_categories = Design.objects.values_list('category', flat=True).distinct()

    def format_category(category):
        return category.replace('_', ' ').title()

    formatted_categories = [{'value': cat, 'display': format_category(cat)} for cat in all_categories]

    context = {
        'mood_board': mood_board,
        'designs': designs,
        'user_type': user_type,
        'designers': all_designers,
        'categories': formatted_categories,
        'no_results': designs.count() == 0,
        'selected_category': category,
        'selected_designer': designer,
        'selected_sqft_range': sqft_range,
    }

    return render(request, 'mood_boards/add_design.html', context)

@login_required
def add_product_to_mood_board(request, pk):
    mood_board = get_object_or_404(MoodBoard, pk=pk)
    products = Product.objects.all()
    
    # Get filter parameters
    category = request.GET.get('category')
    
    # Filter by category
    if category and category != 'all':
        products = products.filter(category=category)
    
    # Get unique categories for the dropdown
    categories = Product.objects.values_list('category', flat=True).distinct()
    
    context = {
        'mood_board': mood_board,
        'products': products,
        'categories': categories,
        'selected_category': category,
    }

    if request.user.is_authenticated:
        user = request.user
        user_type = user.user_type_id.user_type if user.user_type_id else None
        context['user_type'] = user_type
        context['user'] = user

    return render(request, 'mood_boards/add_product.html', context)

@login_required
@require_POST
def add_mood_board_item(request, pk):
    # This function doesn't render a template, so we don't need to pass user_type here
    mood_board = get_object_or_404(MoodBoard, pk=pk, user=request.user)
    item_type = request.POST.get('item_type')
    item_id = request.POST.get('item_id')

    if item_type == 'design':
        design = get_object_or_404(Design, pk=item_id)
        item = MoodBoardItem.objects.create(
            mood_board=mood_board,
            item_type='design',
            design=design,
            position_x=0,
            position_y=0
        )
    elif item_type == 'product':
        product = get_object_or_404(Product, pk=item_id)
        item = MoodBoardItem.objects.create(
            mood_board=mood_board,
            item_type='product',
            product=product,
            position_x=0,
            position_y=0
        )
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid item type'})

    return JsonResponse({
        'status': 'success',
        'item_id': item.id,
        'image_url': item.image_url,
        'caption': item.caption,
        'position_x': item.position_x,
        'position_y': item.position_y
    })

@login_required
@require_POST
def update_item_position(request, pk):
    # This function doesn't render a template, so we don't need to pass user_type here
    item = get_object_or_404(MoodBoardItem, pk=pk, mood_board__user=request.user)
    position_x = request.POST.get('position_x')
    position_y = request.POST.get('position_y')
    
    if position_x is not None and position_y is not None:
        try:
            item.position_x = int(float(position_x))
            item.position_y = int(float(position_y))
            item.save()
            return JsonResponse({'status': 'success'})
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid position data'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Missing position data'}, status=400)

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def delete_mood_board_item(request, pk):
    try:
        item = MoodBoardItem.objects.get(pk=pk)
        item.delete()
        return JsonResponse({'status': 'success'})
    except MoodBoardItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)