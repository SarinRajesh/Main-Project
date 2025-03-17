from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # your existing URL patterns
    path('', views.index, name='index'),  # Make index the root URL
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
    
path('delete-portfolio/<int:portfolio_id>/', views.delete_portfolio, name='delete_portfolio'),
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
    path('admin_page/add_deliveryboy/', views.add_deliveryboy, name='add_deliveryboy'),

    path('delivery_boy/index', views.deliveryboy_index, name='deliveryboy_index'),
    path('delivery_boy/delivery', views.delivery, name='delivery'),
    path('delivery_boy/account', views.account, name='account'),

    path('customers_table/', views.customers_table, name='customers_table'),
    path('designers_table/', views.designers_table, name='designers_table'),
    path('admin_page/designs_table/', views.designs_table, name='designs_table'),
    path('admin_page/consultations_table/', views.consultations_table, name='consultations_table'),
    path('admin_page/products_table/', views.products_table, name='products_table'),
    path('admin_page/admin_index/', views.admin_index, name='admin_index'),
     path('admin_page/projects_table/', views.projects_table, name='projects_table'),
 
    path('clear_cart/', views.clear_cart, name='clear_cart'),
     path('create_order_from_product/', views.create_order_from_product, name='create_order_from_product'),
    path('create_order_from_cart/', views.create_order_from_cart, name='create_order_from_cart'),
    path('my_orders/', views.orders, name='my_orders'),
    path('schedule-consultation/', views.schedule_consultation, name='schedule_consultation'),
 path('remove_scheduled_date/', views.remove_scheduled_date, name='remove_scheduled_date'),  # New URL pattern
 path('send_chat_message/', views.send_chat_message, name='send_chat_message'),
    path('get_chat_messages/', views.get_chat_messages, name='get_chat_messages'),
    path('clear-chat-history/', views.clear_chat_history, name='clear_chat_history'),
    
path('admin_page/designs-table/', views.designs_table, name='designs_table'),
path('admin_page/orders-table/', views.orders_table, name='orders_table'),
path('admin_page/product_sales_analytics/', views.product_sales_analytics, name='product_sales_analytics'),

path('download_receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),

   path('recommend-products/', views.recommend_products_by_color, name='recommend_products_by_color'),

   path('mood-boards/', views.mood_board_list, name='mood_board_list'),
    path('mood-boards/create/', views.create_mood_board, name='create_mood_board'),
    path('mood-boards/<int:pk>/', views.mood_board_detail, name='mood_board_detail'),
    path('mood-boards/<int:pk>/add-item/', views.add_mood_board_item, name='add_mood_board_item'),
    path('mood-board-items/<int:pk>/update-position/', views.update_item_position, name='update_item_position'),
    path('mood-boards/<int:pk>/', views.mood_board_detail, name='mood_board_detail'),
    path('mood-boards/<int:pk>/add-design/', views.add_design_to_mood_board, name='add_design_to_mood_board'),
    path('mood-boards/<int:pk>/add-product/', views.add_product_to_mood_board, name='add_product_to_mood_board'),
    path('mood-boards/<int:pk>/add-item/', views.add_mood_board_item, name='add_mood_board_item'),
   path('delete-mood-board-item/<int:pk>/', views.delete_mood_board_item, name='delete_mood_board_item'),
    path('mood-boards/<int:pk>/delete/', views.delete_mood_board, name='delete_mood_board'),
 path('my_projects/', views.my_projects, name='my_projects'),
  path('project/<int:project_id>/', views.project, name='project'),
path('projects_manage/', views.projects_manage, name='projects_manage'),


path('virtual-room/', views.virtual_room_designer, name='virtual_room_designer'),
path('create_room/', views.create_room, name='create_room'),
path('get_all_rooms/', views.get_all_rooms, name='get_all_rooms'),
path('get_room/<int:room_id>/', views.get_room, name='get_room'),
path('delete_room/<int:room_id>/', views.delete_room, name='delete_room'),

path('api/user-info/', views.get_user_info, name='user_info'),
path('upload-room-model/', views.upload_room_model, name='upload_room_model'),
path('get-room-models/', views.get_room_models, name='get_room_models'),
path('delete-room-model/<int:model_id>/', views.delete_room_model, name='delete_room_model'),
path('update-model-position/', views.update_model_position, name='update_model_position'),
path('add-model-to-room/', views.add_model_to_room, name='add_model_to_room'),
path('get-room-models/<int:room_id>/', views.get_room_models_for_room, name='get_room_models_for_room'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
