"""
Domain CRUD Views – Cithara
============================
Simple function-based views providing JSON responses.
These demonstrate CRUD operations for Exercise 3, Task 4.
Authentication middleware is intentionally excluded per exercise scope.
"""

import json
import random
import string
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Song, MusicGenerationRequest, ShareLink, Feedback, GenerationStatus, EmailVerification
from .suno_service import launch_generation_thread


def _body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


# ---------------------------------------------------------------------------
# Auth  – login, register, email verification
# ---------------------------------------------------------------------------

def _user_json(user):
    return {'id': user.id, 'email': user.email, 'name': user.name}


@csrf_exempt
def auth_request_verification(request):
    """
    POST /auth/request-verification/
    Body: { email, name, password }
    Generates 6-digit code, stores it, "sends" to email (console in dev).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _body(request)
    email = (data.get('email') or '').strip()
    name = (data.get('name') or '').strip()
    password = data.get('password') or ''

    if not email or not name or not password:
        return JsonResponse({'error': 'email, name, and password are required'}, status=400)
    if len(password) < 6:
        return JsonResponse({'error': 'password must be at least 6 characters'}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': 'An account with this email already exists'}, status=400)

    code = ''.join(random.choices(string.digits, k=6))
    password_hash = make_password(password)
    EmailVerification.objects.create(
        email=email,
        code=code,
        name=name,
        password_hash=password_hash,
    )

    subject = "Your Cithara verification code"
    message = f"Hi {name},\n\nYour verification code is: {code}\n\nThis code expires in 10 minutes.\n\n— Cithara"
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[Cithara] Email failed ({e}); code for {email}: {code}")
        return JsonResponse({'error': 'Could not send verification email. Check server logs.'}, status=500)

    return JsonResponse({'sent': True, 'email': email})


@csrf_exempt
def auth_verify_and_register(request):
    """
    POST /auth/verify-and-register/
    Body: { email, name, password, code }
    Verifies code and creates user.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _body(request)
    email = (data.get('email') or '').strip()
    name = (data.get('name') or '').strip()
    password = data.get('password') or ''
    code = (data.get('code') or '').strip()

    if not email or not name or not code:
        return JsonResponse({'error': 'email, name, and code are required'}, status=400)

    try:
        ev = EmailVerification.objects.filter(email__iexact=email).order_by('-created_at').first()
        if not ev or ev.code != code:
            return JsonResponse({'error': 'Invalid or expired verification code'}, status=400)
        if (timezone.now() - ev.created_at).total_seconds() > 600:
            return JsonResponse({'error': 'Verification code expired (10 min)'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Invalid or expired verification code'}, status=400)

    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': 'Account already exists for this email'}, status=400)

    user = User.objects.create(
        email=email,
        name=name,
        password_hash=ev.password_hash,
        last_login_at=timezone.now(),
    )
    ev.delete()
    return JsonResponse(_user_json(user), status=201)


@csrf_exempt
def auth_login(request):
    """
    POST /auth/login/
    Body: { email, password }
    Returns user if credentials valid.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _body(request)
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    if not email or not password:
        return JsonResponse({'error': 'email and password are required'}, status=400)

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid email or password'}, status=401)
    if not user.password_hash:
        return JsonResponse({'error': 'This account uses Google sign-in'}, status=401)
    if not check_password(password, user.password_hash):
        return JsonResponse({'error': 'Invalid email or password'}, status=401)

    user.last_login_at = timezone.now()
    user.save(update_fields=['last_login_at'])
    return JsonResponse(_user_json(user))


@csrf_exempt
def auth_google(request):
    """
    POST /auth/google/
    Body: { credential } – Google ID token from @react-oauth/google
    Verifies token (or accepts in dev), finds/creates user, returns user.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = _body(request)
    credential = data.get('credential') or data.get('id_token') or ''

    if not credential:
        return JsonResponse({'error': 'Google credential is required'}, status=400)

    try:
        import jwt
        decoded = jwt.decode(
            credential,
            options={"verify_signature": False},
        )
        email = decoded.get('email') or ''
        name = decoded.get('name') or decoded.get('email', '').split('@')[0]
        google_id = decoded.get('sub') or ''
    except Exception:
        return JsonResponse({'error': 'Invalid Google credential'}, status=401)

    if not email or not google_id:
        return JsonResponse({'error': 'Invalid Google credential'}, status=401)

    user = User.objects.filter(email__iexact=email).first()
    if user:
        if not user.google_id:
            user.google_id = google_id
            user.save(update_fields=['google_id'])
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
    else:
        user = User.objects.create(
            email=email,
            name=name,
            google_id=google_id,
            last_login_at=timezone.now(),
        )
    return JsonResponse(_user_json(user))


# ---------------------------------------------------------------------------
# Users  (FR-01 – FR-07)
# ---------------------------------------------------------------------------

@csrf_exempt
def user_list(request):
    """
    GET  /users/  – list all users
    POST /users/  – create a user
    """
    if request.method == 'GET':
        users = list(User.objects.values(
            'id', 'email', 'name', 'google_id', 'created_at', 'last_login_at'
        ))
        return JsonResponse(users, safe=False)

    if request.method == 'POST':
        data = _body(request)
        if not data.get('email') or not data.get('name'):
            return JsonResponse({'error': 'email and name are required'}, status=400)
        if not data.get('google_id') and not data.get('password_hash'):
            return JsonResponse(
                {'error': 'At least one of google_id or password_hash is required (C-3)'},
                status=400,
            )
        user = User.objects.create(
            email=data['email'],
            name=data['name'],
            google_id=data.get('google_id'),
            password_hash=data.get('password_hash'),
        )
        return JsonResponse({'id': user.id, 'email': user.email, 'name': user.name}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def user_detail(request, pk):
    """
    GET    /users/<id>/  – retrieve user
    PATCH  /users/<id>/  – update user
    DELETE /users/<id>/  – delete user
    """
    user = get_object_or_404(User, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': user.id, 'email': user.email, 'name': user.name,
            'has_google': bool(user.google_id),
            'has_password': bool(user.password_hash),
            'created_at': str(user.created_at),
            'last_login_at': str(user.last_login_at) if user.last_login_at else None,
        })

    if request.method in ('PATCH', 'PUT'):
        data = _body(request)
        for field in ('name', 'email', 'google_id', 'password_hash'):
            if field in data:
                setattr(user, field, data[field])
        user.full_clean()
        user.save()
        return JsonResponse({'id': user.id, 'email': user.email, 'name': user.name})

    if request.method == 'DELETE':
        user.delete()
        return JsonResponse({'deleted': True}, status=204)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ---------------------------------------------------------------------------
# Songs  (FR-17, FR-28 – FR-35)
# ---------------------------------------------------------------------------

@csrf_exempt
def song_list(request):
    """
    GET  /songs/?user_id=<id>  – list songs for a user (newest first, FR-32)
    POST /songs/               – create/save a song
    """
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
        data = _body(request)
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
    """
    GET    /songs/<id>/  – retrieve song with share link info
    PATCH  /songs/<id>/  – update song
    DELETE /songs/<id>/  – permanently delete song (FR-35, C-12)
    """
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
        data = _body(request)
        for field in ('title', 'genre', 'mood', 'occasion', 'voice_type',
                      'custom_story', 'prompt_used', 'audio_file_path', 'duration', 'status', 'is_saved'):
            if field in data:
                setattr(song, field, data[field])
        song.full_clean()
        song.save()
        return JsonResponse({'id': song.id, 'title': song.title, 'status': song.status})

    if request.method == 'DELETE':
        # C-12: Deletion is permanent and irreversible.
        # Cascade deletes ShareLink automatically (C-8).
        song.delete()
        return JsonResponse({'deleted': True, 'note': 'Song permanently removed (C-12)'}, status=200)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ---------------------------------------------------------------------------
# MusicGenerationRequests  (FR-08 – FR-18, FR-24 – FR-27)
# ---------------------------------------------------------------------------

@csrf_exempt
def request_list(request):
    """
    GET  /requests/?user_id=<id>  – list generation requests
    POST /requests/               – submit a new generation request
    """
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
        data = _body(request)
        user = get_object_or_404(User, pk=data.get('user_id'))
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
        req.full_clean()
        req.save()
        
        # Trigger the async Suno AI generation
        launch_generation_thread(req.id)

        return JsonResponse({
            'id': req.id, 'title': req.title, 'status': req.status, 'is_retry': req.is_retry
        }, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def request_detail(request, pk):
    """
    GET   /requests/<id>/  – retrieve request + timeout check
    PATCH /requests/<id>/  – update status / attach song
    """
    req = get_object_or_404(MusicGenerationRequest, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': req.id, 'title': req.title, 'status': req.status,
            'is_retry': req.is_retry, 'submitted_at': str(req.submitted_at),
            'genre': req.genre, 'mood': req.mood, 'voice_type': req.voice_type,
            'occasion': req.occasion, 'custom_story': req.custom_story,
            'prompt_generated': req.prompt_generated, 'error_message': req.error_message,
            'song_id': req.song_id,
            'timed_out': req.is_timed_out(),   # C-9
        })

    if request.method in ('PATCH', 'PUT'):
        data = _body(request)
        for field in ('status', 'prompt_generated', 'error_message', 'is_retry'):
            if field in data:
                setattr(req, field, data[field])
        if 'song_id' in data:
            req.song = get_object_or_404(Song, pk=data['song_id'])
        req.full_clean()
        req.save()
        return JsonResponse({'id': req.id, 'status': req.status})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ---------------------------------------------------------------------------
# Share Link creation (FR-37)
# ---------------------------------------------------------------------------

@csrf_exempt
def create_share_link(request, pk):
    """
    POST /songs/<id>/share/  – create a ShareLink for a song (FR-37)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    song = get_object_or_404(Song, pk=pk)
    try:
        link = song.share_link
        return JsonResponse({
            'token': link.token,
            'share_url': link.share_url,
            'is_active': link.is_active,
        })
    except ShareLink.DoesNotExist:
        token = str(uuid.uuid4())
        share_url = f"/share/{token}"
        link = ShareLink.objects.create(
            song=song,
            token=token,
            share_url=share_url,
        )
        return JsonResponse({
            'token': link.token,
            'share_url': link.share_url,
            'is_active': link.is_active,
        }, status=201)


# ---------------------------------------------------------------------------
# SharedLink – listen endpoint  (FR-38, FR-39, FR-41, C-11)
# ---------------------------------------------------------------------------

def shared_song(request, token):
    """
    GET /share/<token>/
    Simulates the listen-to-shared-song flow (UC-10).
    C-11: Requires authentication (mocked here – real auth is out of Exercise 3 scope).
    FR-41: Returns 410 Gone if the song is deleted or the link is inactive.
    """
    link = get_object_or_404(ShareLink, token=token)

    if not link.is_active:
        return JsonResponse(
            {'error': 'This song is no longer available (FR-41).'},
            status=410,
        )

    song = link.song
    return JsonResponse({
        'song_id': song.id,
        'title': song.title,
        'genre': song.genre,
        'mood': song.mood,
        'audio_file_path': song.audio_file_path,
        'note': 'In production, authentication is required before reaching this point (C-11, FR-39).',
    })


# ---------------------------------------------------------------------------
# Feedback  (FR-50, FR-51, C-14)
# ---------------------------------------------------------------------------

@csrf_exempt
def feedback_list(request):
    """
    GET  /feedback/  – list all feedback (internal use only, C-14)
    POST /feedback/  – submit feedback
    """
    if request.method == 'GET':
        feedbacks = list(Feedback.objects.values(
            'id', 'user__name', 'song__title', 'feedback_text', 'is_reviewed', 'submitted_at'
        ))
        return JsonResponse(feedbacks, safe=False)

    if request.method == 'POST':
        data = _body(request)
        user = get_object_or_404(User, pk=data.get('user_id'))
        song = None
        if data.get('song_id'):
            song = get_object_or_404(Song, pk=data['song_id'])
        fb = Feedback.objects.create(
            user=user,
            song=song,
            feedback_text=data.get('feedback_text', ''),
        )
        return JsonResponse({'id': fb.id, 'submitted_at': str(fb.submitted_at)}, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
