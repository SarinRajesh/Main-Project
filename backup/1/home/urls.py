from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('', views.signin, name='signin'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('accounts/', include('allauth.urls')),  # Includes allauth URLs for authentication
]
