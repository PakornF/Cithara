from django.db import models


class ShareLink(models.Model):
    """Secure tokenized URL for sharing a saved Song (FR-37)."""

    song = models.OneToOneField(
        'domain.Song',
        on_delete=models.CASCADE,
        related_name='share_link',
        help_text='C-8: Composition – ShareLink is deleted with its Song.',
    )
    token = models.CharField(max_length=255, unique=True)
    share_url = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Reserved for future link-expiry (Open Issue 5). Currently null (Assumption 5).',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Set False when the parent Song is deleted (FR-41).',
    )

    class Meta:
        verbose_name = 'Share Link'
        verbose_name_plural = 'Share Links'

    def __str__(self):
        return f'ShareLink for Song#{self.song_id} - active={self.is_active}'
