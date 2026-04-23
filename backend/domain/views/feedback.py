from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import Feedback, Song, User
from ._helpers import parse_body


@csrf_exempt
def feedback_list(request):
    """GET /feedback/ — list all feedback; POST /feedback/ — submit feedback."""
    if request.method == 'GET':
        feedbacks = list(Feedback.objects.values(
            'id', 'user__name', 'song__title', 'feedback_text', 'is_reviewed', 'submitted_at'
        ))
        return JsonResponse(feedbacks, safe=False)

    if request.method == 'POST':
        data = parse_body(request)
        user = get_object_or_404(User, pk=data.get('user_id'))
        song = get_object_or_404(Song, pk=data['song_id']) if data.get('song_id') else None
        fb = Feedback.objects.create(
            user=user,
            song=song,
            feedback_text=data.get('feedback_text', ''),
        )
        return JsonResponse({'id': fb.id, 'submitted_at': str(fb.submitted_at)}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
