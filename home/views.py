from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import make_password
from .models import UserType, Consultation, Users, Design, Amount, Product, Cart
from .decorators import nocache
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from allauth.socialaccount.models import SocialAccount
from django.views.decorators.csrf import csrf_exempt
import random



class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp)

token_generator = CustomTokenGenerator()

@login_required
@nocache
def index(request):
    if request.user.is_authenticated:
        user = request.user
        user_type = user.user_type_id.user_type if user.user_type_id else None
        return render(request, 'index.html', {'user': user, 'user_type': user_type})
    return render(request, 'index.html')




def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return custom_login_redirect(request)
        else:
            return HttpResponse("Invalid username or password.")
    
    return render(request, 'signin.html')

def custom_login_redirect(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('signin')

    # Check if the user has set their user type
    if not user.user_type_id:
        return redirect('usertype')

    user_type = user.user_type_id.user_type
    if user_type == 'Admin':
        return redirect('tables')
    else:
        return redirect('index')

    return redirect('index')


@login_required
def usertype(request):
    user = request.user
    if request.method == 'POST':
        user_type_id = request.POST.get('user_type_id')
        if user_type_id:
            try:
                user_type = UserType.objects.get(id=user_type_id)
                user.user_type_id = user_type
                user.save()
                request.session['user_type_set'] = True  # Mark user type as set
                return custom_login_redirect(request)  # Redirect based on user type after setting user type
            except UserType.DoesNotExist:
                messages.error(request, 'Invalid user type selected.')
        else:
            messages.error(request, 'No user type selected.')
    
    user_types = UserType.objects.all()
    return render(request, 'usertype.html', {'user_types': user_types})


def generate_otp():
    return random.randint(100000, 999999)

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

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

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if otp == str(session_otp):
            user_data = request.session.get('user_data')
            if user_data:
                try:
                    # Create a new user with the provided data
                    user = Users.objects.create(
                        name=user_data['name'],
                        phone=user_data['phone'],
                        email=user_data['email'],
                        username=user_data['username'],
                        password=make_password(user_data['password']),  # Hash the password
                    )
                    user.save()

                    # Log the user in
                    backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
                    user = authenticate(username=user_data['username'], password=user_data['password'], backend=backend)
                    if user is not None:
                        login(request, user)
                    
                    # Clear user data from session
                    request.session.pop('user_data', None)

                    return redirect('usertype')
                except Exception as e:
                    messages.error(request, f"Error creating account: {str(e)}")
            else:
                messages.error(request, "User data not found in session. Please sign up again.")
                return redirect('signup')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')



@nocache
@login_required
def profile(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.address = request.POST.get('address')
        user.home_town = request.POST.get('home_town')
        user.district = request.POST.get('district')
        user.state = request.POST.get('state')
        user.pincode = request.POST.get('pincode')
        if 'photo' in request.FILES:
            user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    return render(request, 'profile.html', {'user': user, 'user_type': user_type})



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
def dashboard(request):
    return render(request, 'admin_page/dashboard.html')

@nocache
@login_required
def tables(request):
    users = Users.objects.all()
    user_types = UserType.objects.all()
    designs = Design.objects.all()
    products = Product.objects.all()
    consultations = Consultation.objects.all()

    return render(request, 'admin_page/tables.html', {
        'users': users,
        'user_types': user_types,
        'designs': designs,
        'products': products,
        'consultations': consultations
    })
@login_required
@nocache
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        amount_value = request.POST.get('amount')
        image = request.FILES.get('image')
        category = request.POST.get('category')

        amount = Amount(amount=amount_value)
        amount.save()

        portfolio = Product(
            name=name,
            description=description,
            amount=amount,
            category=category,
            image=image
        )
        portfolio.save()

        return redirect('add_product')

    return render(request, 'admin_page/add_product.html')

@login_required
@nocache
def add_portfolio(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        amount_value = request.POST.get('amount')
        image = request.FILES.get('image')

        amount = Amount(amount=amount_value)
        amount.save()

        portfolio = Design(
            designer_id=request.user,
            name=name,
            description=description,
            amount=amount,
            image=image
        )
        portfolio.save()

        return redirect('portfolio')

    return render(request, 'add_portfolio.html', {'user_type': user_type})

@nocache
@login_required
def portfolio(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    portfolios = Design.objects.all()
    return render(request, 'portfolio.html', {'portfolios': portfolios, 'user_type': user_type})

@nocache
@login_required
def shop(request):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    
    product = Product.objects.all()
    return render(request, 'shop.html', {'products': product, 'user_type': user_type})

from django.shortcuts import render, get_object_or_404

@nocache
@login_required
def portfolio_details(request, portfolio_id):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    portfolio = get_object_or_404(Design.objects.select_related('designer_id'), id=portfolio_id)

    if request.method == 'POST':
        # Check if the request is to reject a consultation
        if 'reject' in request.POST:
            # Delete the consultation entry if it exists
            Consultation.objects.filter(
                design_id=portfolio_id,
                customer_id=user,
                designer_id=portfolio.designer_id
            ).delete()

            messages.success(request, 'Consultation request rejected.')
            return redirect('portfolio_details', portfolio_id=portfolio_id)
        
        # Extract data from the hidden form for booking a consultation
        proposal = request.POST.get('proposal')
        consultation_status = request.POST.get('consultation_status')
        design_id = request.POST.get('design_id')
        customer_id = request.POST.get('customer_id')
        designer_id = request.POST.get('designer_id')

        # Check if there's an existing consultation
        existing_consultation = Consultation.objects.filter(
            design_id=design_id,
            customer_id=customer_id,
            designer_id=designer_id
        ).first()

        if not existing_consultation:
            # Create a new consultation entry
            consultation = Consultation(
                customer_id=Users.objects.get(id=customer_id),
                designer_id=Users.objects.get(id=designer_id),
                design_id=Design.objects.get(id=design_id),
                consultation_status=consultation_status,
                proposal=proposal
            )
            consultation.save()
            messages.success(request, 'Consultation request submitted successfully.')
        else:
            messages.info(request, 'Consultation already booked.')

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
        'consultation_status': consultation_status
    }

    return render(request, 'portfolio_details.html', context)


from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

@nocache
@login_required
def product(request, product_id):
    user = request.user
    user_type = user.user_type_id.user_type if user.user_type_id else None
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        if 'product_id' in request.POST:
            product_id = int(request.POST.get('product_id'))
            status = request.POST.get('status')
            quantity = int(request.POST.get('quantity', 1))
            amount_value = request.POST.get('amount')
            
            if status == 'Added':
                product_instance = get_object_or_404(Product, id=product_id)
                
                try:
                    # Try to convert the amount to a Decimal
                    unit_price = Decimal(amount_value)
                except (InvalidOperation, TypeError):
                    # If conversion fails, use the product's amount
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

                # Store success message in session
                request.session['cart_message'] = 'Product added to cart successfully.'
                return redirect('product', product_id=product_id)

    # Get and clear the cart message from the session
    cart_message = request.session.pop('cart_message', None)

    context = {
        'product': product,
        'user_type': user_type,
        'cart_message': cart_message,
    }

    return render(request, 'product.html', context)


@nocache
@login_required
def cart(request):
    cart_items = Cart.objects.filter(user_id=request.user)
    
    # Calculate total price
    total_price = sum(item.amount for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user_id=request.user.id)
    cart_item.delete()
    return redirect('cart')

from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json

@nocache
@require_POST
@csrf_exempt
def update_cart_quantity(request):
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
            'total_price': total_price,
            'item_total': cart_item.amount
        })
    except Cart.DoesNotExist:
        return JsonResponse({'success': False}, status=400)

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
    
    context = {
        'consultations': consultations,
        'user_type': user_type,
    }
    return render(request, 'consultations.html', context)