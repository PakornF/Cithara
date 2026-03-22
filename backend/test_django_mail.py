import os
import sys
import django
import ssl
import certifi

_orig_create_default_context = ssl.create_default_context

def custom_create_default_context(purpose=ssl.Purpose.SERVER_AUTH, *, cafile=None, capath=None, cadata=None):
    if cafile is None:
        cafile = certifi.where()
    return _orig_create_default_context(purpose=purpose, cafile=cafile, capath=capath, cadata=cadata)

ssl.create_default_context = custom_create_default_context


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cithara.settings')
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    print("dotenv not installed")

django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"EMAIL_BACKEND={settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST={settings.EMAIL_HOST}")
try:
    send_mail(
        "Test Subject 2",
        "Test message.",
        settings.DEFAULT_FROM_EMAIL,
        ["pfudul@gmail.com"],
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
