from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import MusicGenerationRequest, Song, User
from ..services import launch_generation_thread
from ._helpers import parse_body


@csrf_exempt
def request_list(request):
    """GET /requests/?user_id=<id> — list requests; POST /requests/ — submit new request."""
    if request.method == 'GET':
        qs = MusicGenerationRequest.objects.select_related('user', 'song')
        user_id = request.GET.get('user_id')
        if user_id:
            qs = qs.filter(user_id=user_id)
        reqs = list(qs.values(
            'id', 'title', 'status', 'is_retry', 'submitted_at',
            'genre', 'mood', 'voice_type', 'occasion', 'error_message',
            'user__name', 'song__id'
        ))
        return JsonResponse(reqs, safe=False)

    if request.method == 'POST':
        data = parse_body(request)
        user_id = data.get('user_id')
        if user_id is None:
            return JsonResponse({'error': 'user_id is required'}, status=400)
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'user_id must be an integer'}, status=400)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': f'User with id {user_id} does not exist'}, status=400)

        req = MusicGenerationRequest(
            user=user,
            title=data.get('title', ''),
            genre=data.get('genre', ''),
            mood=data.get('mood', ''),
            voice_type=data.get('voice_type', ''),
            occasion=data.get('occasion', ''),
            custom_story=data.get('custom_story'),
            is_retry=data.get('is_retry', False),
        )
        try:
            req.full_clean()
        except ValidationError as exc:
            return JsonResponse(
                {'error': exc.message_dict if hasattr(exc, 'message_dict') else exc.messages},
                status=400,
            )
        req.save()
        launch_generation_thread(req.id)

        return JsonResponse(
            {'id': req.id, 'title': req.title, 'status': req.status, 'is_retry': req.is_retry},
            status=201,
        )

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def request_detail(request, pk):
    """GET/PATCH /requests/<id>/"""
    req = get_object_or_404(MusicGenerationRequest, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': req.id, 'title': req.title, 'status': req.status,
            'is_retry': req.is_retry, 'submitted_at': str(req.submitted_at),
            'genre': req.genre, 'mood': req.mood, 'voice_type': req.voice_type,
            'occasion': req.occasion, 'custom_story': req.custom_story,
            'prompt_generated': req.prompt_generated, 'error_message': req.error_message,
            'song_id': req.song_id,
            'timed_out': req.is_timed_out(),
        })

    if request.method in ('PATCH', 'PUT'):
        data = parse_body(request)
        for field in ('status', 'prompt_generated', 'error_message', 'is_retry'):
            if field in data:
                setattr(req, field, data[field])
        if 'song_id' in data:
            req.song = get_object_or_404(Song, pk=data['song_id'])
        req.full_clean()
        req.save()
        return JsonResponse({'id': req.id, 'status': req.status})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
