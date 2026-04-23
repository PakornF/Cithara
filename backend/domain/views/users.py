from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..models import User
from ._helpers import parse_body


@csrf_exempt
def user_list(request):
    """GET /users/ — list all users; POST /users/ — create a user."""
    if request.method == 'GET':
        users = list(User.objects.values(
            'id', 'email', 'name', 'google_id', 'created_at', 'last_login_at'
        ))
        return JsonResponse(users, safe=False)

    if request.method == 'POST':
        data = parse_body(request)
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
    """GET/PATCH/DELETE /users/<id>/"""
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
        data = parse_body(request)
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
