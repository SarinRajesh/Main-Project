from django.urls import path
from . import views

urlpatterns = [
    path('virtual-room/', views.virtual_room_designer, name='virtual_room_designer'),
    path('virtual-room/create/', views.create_room, name='create_room'),
    path('virtual-room/add-item/', views.add_room_item, name='add_room_item'),
    path('virtual-room/update-item/', views.update_item_position, name='update_item_position'),
] 