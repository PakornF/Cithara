from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ..models import ShareLink


def shared_song(request, token):
    """GET /share/<token>/ — public listen endpoint."""
    link = get_object_or_404(ShareLink, token=token)

    if not link.is_active:
        return JsonResponse({'error': 'This song is no longer available (FR-41).'}, status=410)

    song = link.song
    return JsonResponse({
        'song_id': song.id,
        'title': song.title,
        'genre': song.genre,
        'mood': song.mood,
        'audio_file_path': song.audio_file_path,
    })
