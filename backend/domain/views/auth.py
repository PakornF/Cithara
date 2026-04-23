import random
import string

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from ..models import EmailVerification, User
from ._helpers import parse_body


def _user_json(user):
    return {'id': user.id, 'email': user.email, 'name': user.name}


@csrf_exempt
def auth_request_verification(request):
    """POST /auth/request-verification/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = parse_body(request)
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
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception as e:
        print(f"[Cithara] Email failed ({e}); code for {email}: {code}")
        return JsonResponse({'error': 'Could not send verification email. Check server logs.'}, status=500)

    return JsonResponse({'sent': True, 'email': email})


@csrf_exempt
def auth_verify_and_register(request):
    """POST /auth/verify-and-register/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = parse_body(request)
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
    """POST /auth/login/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = parse_body(request)
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
    """POST /auth/google/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = parse_body(request)
    credential = data.get('credential') or data.get('id_token') or ''

    if not credential:
        return JsonResponse({'error': 'Google credential is required'}, status=400)

    try:
        import jwt
        decoded = jwt.decode(credential, options={"verify_signature": False})
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
