from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # your existing URL patterns
    path('', views.index, name='index'),
    path('cart/', views.cart, name='cart'),
    path('consultations/', views.consultations, name='consultations'),
    path('edit-portfolio/<int:portfolio_id>/', views.edit_portfolio, name='edit_portfolio'),
 path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
   path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<int:portfolio_id>/', views.portfolio_details, name='portfolio_details'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('accounts/', include('allauth.urls')),  # Includes allauth URLs for authentication
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/', views.profile, name='profile'),
    path('usertype/', views.usertype, name='usertype'),
    path('check_email/', views.check_email, name='check_email'),
    path('check_username/', views.check_username, name='check_username'),
    path('custom_login_redirect/', views.custom_login_redirect, name='custom_login_redirect'),  # Custom redirect
    path('upload_photo/', views.upload_photo, name='upload_photo'),
    path('add_portfolio/', views.add_portfolio, name='add_portfolio'),
    path('admin_page/add_product/', views.add_product, name='add_product'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tables/', views.tables, name='tables'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
