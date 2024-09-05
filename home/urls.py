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
    path('my_consultations/', views.my_consultations, name='my_consultations'),
    path('edit-portfolio/<int:portfolio_id>/', views.edit_portfolio, name='edit_portfolio'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<int:portfolio_id>/', views.portfolio_details, name='portfolio_details'),
    path('consultation_booking/<int:portfolio_id>/', views.consultation_booking, name='consultation_booking'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('password_reset/', views.request_password_reset, name='request_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('accounts/', include('allauth.urls')),  # Includes allauth URLs for authentication
    path('logout/', views.logout_view, name='logout_view'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('check_email/', views.check_email, name='check_email'),
    path('check_username/', views.check_username, name='check_username'),
    path('custom_login_redirect/', views.custom_login_redirect, name='custom_login_redirect'),  # Custom redirect
    path('upload_photo/', views.upload_photo, name='upload_photo'),
    path('add_portfolio/', views.add_portfolio, name='add_portfolio'),
    path('admin_page/add_product/', views.add_product, name='add_product'),
    path('admin_page/add_designer/', views.add_designer, name='add_designer'),
    path('users_table/', views.users_table, name='users_table'),
    path('admin_page/designs_table/', views.designs_table, name='designs_table'),
    path('admin_page/consultations_table/', views.consultations_table, name='consultations_table'),
    path('admin_page/products_table/', views.products_table, name='products_table'),
    path('admin_page/admin_index/', views.admin_index, name='admin_index'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
     path('create_order_from_product/', views.create_order_from_product, name='create_order_from_product'),
    path('create_order_from_cart/', views.create_order_from_cart, name='create_order_from_cart'),
    path('my_orders/', views.orders, name='my_orders'),
    path('schedule-consultation/', views.schedule_consultation, name='schedule_consultation'),
 path('remove_scheduled_date/', views.remove_scheduled_date, name='remove_scheduled_date'),  # New URL pattern
 path('send_chat_message/', views.send_chat_message, name='send_chat_message'),
    path('get_chat_messages/', views.get_chat_messages, name='get_chat_messages'),
path('admin_page/designs-table/', views.designs_table, name='designs_table'),
path('admin_page/orders-table/', views.orders_table, name='orders_table'),

   path('recommend-products/', views.recommend_products_by_color, name='recommend_products_by_color'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)