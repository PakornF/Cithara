from django.core.exceptions import ValidationError
from django.db import models


class User(models.Model):
    """
    Represents an authenticated person using Cithara.
    Supports dual authentication: Google OAuth (googleId) and manual login
    (passwordHash). At least one must be present (C-3).
    """

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    google_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        help_text="Populated for Google OAuth users (FR-01).",
    )
    password_hash = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Populated for manual-login users (FR-02).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def clean(self):
        """C-3: At least one of google_id or password_hash must be present."""
        if not self.google_id and not self.password_hash:
            raise ValidationError(
                "A User must have at least one authentication method: "
                "google_id (OAuth) or password_hash (manual login)."
            )

    def __str__(self):
        return f"{self.name} <{self.email}>"
