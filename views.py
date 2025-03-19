from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
import os

@login_required
def add_models(request):
    room_models = RoomModel.objects.all().order_by('-id')
    categories = [
        ('furniture', 'Furniture'),
        ('bed', 'Bed'),
        ('window', 'Window'),
        ('door', 'Door'),
        ('decoration', 'Decoration'),
        ('table', 'Table'),
        ('chair', 'Chair'),
        ('lighting', 'Lighting')
    ]
    
    context = {
        'room_models': room_models,
        'categories': categories,
        'user_type': 'admin'  # Add this to ensure proper template rendering
    }
    return render(request, 'admin_page/add_models.html', context)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_room_model(request, model_id):
    try:
        model = RoomModel.objects.get(id=model_id)
        model.delete()
        return JsonResponse({'success': True})
    except RoomModel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Model not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def upload_room_model(request):
    try:
        # Your existing upload logic here
        # ...
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500) 