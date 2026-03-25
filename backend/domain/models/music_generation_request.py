from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .choices import GenerationStatus, Genre, Mood, Occasion, VoiceType


class MusicGenerationRequest(models.Model):
    """Captures structured inputs for a song generation job."""

    user = models.ForeignKey(
        'domain.User',
        on_delete=models.CASCADE,
        related_name='generation_requests',
    )
    song = models.ForeignKey(
        'domain.Song',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generation_requests',
        help_text='Populated once a Song is successfully produced (0..* → 0..1).',
    )

    title = models.CharField(max_length=255, help_text='C-4: Mandatory.')
    genre = models.CharField(max_length=50, choices=Genre.choices)
    mood = models.CharField(max_length=50, choices=Mood.choices)
    voice_type = models.CharField(max_length=10, choices=VoiceType.choices)
    occasion = models.CharField(max_length=50, choices=Occasion.choices)
    custom_story = models.TextField(
        blank=True,
        null=True,
        help_text='Optional (FR-13). Max 1,000 characters (C-5).',
    )

    prompt_generated = models.TextField(
        blank=True,
        null=True,
        help_text='The prompt constructed and sent to Suno AI (FR-17).',
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_retry = models.BooleanField(
        default=False,
        help_text='True when this is a regeneration attempt (FR-24).',
    )
    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text='Populated only on failure/timeout/rejection. Null on success (FR-18, FR-49).',
    )

    class Meta:
        verbose_name = 'Music Generation Request'
        verbose_name_plural = 'Music Generation Requests'
        ordering = ['-submitted_at']

    def clean(self):
        """C-4 + C-5 validation."""
        if not self.title or not self.title.strip():
            raise ValidationError('Title is mandatory before submitting a generation request (C-4).')
        if self.custom_story and len(self.custom_story) > settings.MAX_CUSTOM_STORY_LENGTH:
            raise ValidationError(
                f"custom_story must not exceed {settings.MAX_CUSTOM_STORY_LENGTH} characters (C-5)."
            )

    def is_timed_out(self):
        """C-9: Check whether this request has exceeded the 15-minute timeout."""
        if self.status == GenerationStatus.INPROGRESS:
            elapsed = timezone.now() - self.submitted_at
            return elapsed.total_seconds() > settings.GENERATION_TIMEOUT_MINUTES * 60
        return False

    def __str__(self):
        retry_label = ' [RETRY]' if self.is_retry else ''
        return f"Request#{self.pk}{retry_label} - '{self.title}' ({self.status})"
