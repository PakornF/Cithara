import uuid

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import GenerationStatus, ShareLink, Song, User
from ._helpers import parse_body


@csrf_exempt
def song_list(request):
    """GET /songs/?user_id=<id> — list songs; POST /songs/ — create a song."""
    if request.method == 'GET':
        qs = Song.objects.select_related('owner')
        user_id = request.GET.get('user_id')
        if user_id:
            qs = qs.filter(owner_id=user_id)
        songs = list(qs.values(
            'id', 'title', 'genre', 'mood', 'occasion', 'voice_type',
            'status', 'creation_date', 'owner__name', 'owner__email',
            'is_saved', 'audio_file_path'
        ))
        return JsonResponse(songs, safe=False)

    if request.method == 'POST':
        data = parse_body(request)
        owner = get_object_or_404(User, pk=data.get('owner_id'))
        song = Song(
            owner=owner,
            title=data.get('title', ''),
            genre=data.get('genre', ''),
            mood=data.get('mood', ''),
            occasion=data.get('occasion', ''),
            voice_type=data.get('voice_type', ''),
            custom_story=data.get('custom_story'),
            prompt_used=data.get('prompt_used'),
            audio_file_path=data.get('audio_file_path'),
            status=data.get('status', GenerationStatus.PENDING),
        )
        song.full_clean()
        song.save()
        return JsonResponse({'id': song.id, 'title': song.title, 'status': song.status}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def song_detail(request, pk):
    """GET/PATCH/DELETE /songs/<id>/"""
    song = get_object_or_404(Song, pk=pk)

    if request.method == 'GET':
        share = None
        try:
            share = {'token': song.share_link.token, 'is_active': song.share_link.is_active}
        except ShareLink.DoesNotExist:
            pass
        return JsonResponse({
            'id': song.id, 'title': song.title, 'genre': song.genre,
            'mood': song.mood, 'occasion': song.occasion, 'voice_type': song.voice_type,
            'status': song.status, 'prompt_used': song.prompt_used,
            'audio_file_path': song.audio_file_path, 'duration': song.duration,
            'creation_date': str(song.creation_date),
            'owner': {'id': song.owner_id, 'name': song.owner.name},
            'share_link': share,
        })

    if request.method in ('PATCH', 'PUT'):
        data = parse_body(request)
        for field in ('title', 'genre', 'mood', 'occasion', 'voice_type',
                      'custom_story', 'prompt_used', 'audio_file_path', 'duration', 'status', 'is_saved'):
            if field in data:
                setattr(song, field, data[field])
        song.full_clean()
        song.save()
        return JsonResponse({'id': song.id, 'title': song.title, 'status': song.status})

    if request.method == 'DELETE':
        # C-12: permanent; C-8: ShareLink cascade-deleted automatically
        song.delete()
        return JsonResponse({'deleted': True, 'note': 'Song permanently removed (C-12)'}, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def create_share_link(request, pk):
    """POST /songs/<id>/share/ — create or return existing ShareLink."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    song = get_object_or_404(Song, pk=pk)
    try:
        link = song.share_link
        return JsonResponse({'token': link.token, 'share_url': link.share_url, 'is_active': link.is_active})
    except ShareLink.DoesNotExist:
        token = str(uuid.uuid4())
        link = ShareLink.objects.create(song=song, token=token, share_url=f"/share/{token}")
        return JsonResponse({'token': link.token, 'share_url': link.share_url, 'is_active': link.is_active}, status=201)
