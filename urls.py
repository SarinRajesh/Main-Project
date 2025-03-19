from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('virtual-room/', views.virtual_room_designer, name='virtual_room_designer'),
    path('virtual-room/create/', views.create_room, name='create_room'),
    path('virtual-room/add-item/', views.add_room_item, name='add_room_item'),
    path('virtual-room/update-item/', views.update_item_position, name='update_item_position'),
    path('delete-room-model/<int:model_id>/', views.delete_room_model, name='delete_room_model'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 