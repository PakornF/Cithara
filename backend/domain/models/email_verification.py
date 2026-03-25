from django.db import models


class EmailVerification(models.Model):
    """Temporary code sent to email for account verification."""

    email = models.EmailField(db_index=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Email Verification'
        verbose_name_plural = 'Email Verifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"Verification for {self.email}"
