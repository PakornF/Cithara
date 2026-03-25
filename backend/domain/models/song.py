from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .choices import GenerationStatus, Genre, Mood, Occasion, VoiceType


class Song(models.Model):
    """Represents an AI-generated audio piece."""

    owner = models.ForeignKey(
        'domain.User',
        on_delete=models.CASCADE,
        related_name='songs',
        help_text='C-1: A Song belongs to exactly one User.',
    )
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=50, choices=Genre.choices)
    mood = models.CharField(max_length=50, choices=Mood.choices)
    occasion = models.CharField(max_length=50, choices=Occasion.choices)
    voice_type = models.CharField(max_length=10, choices=VoiceType.choices)
    custom_story = models.TextField(
        blank=True,
        null=True,
        help_text='Optional (FR-13). Max 1,000 characters (C-5).',
    )
    prompt_used = models.TextField(
        blank=True,
        null=True,
        help_text='Stored on Song for display without joining back to request (US-17).',
    )
    audio_file_path = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        help_text='C-7: Only populated when GenerationStatus = Completed.',
    )
    duration = models.IntegerField(
        null=True,
        blank=True,
        help_text='Duration in seconds. Only populated after successful generation (C-7).',
    )
    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
    )
    is_saved = models.BooleanField(
        default=False,
        help_text='True if the user explicitly saved this to their library.',
    )
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
        ordering = ['-creation_date']

    def clean(self):
        """C-5: custom_story must not exceed 1,000 characters."""
        if self.custom_story and len(self.custom_story) > settings.MAX_CUSTOM_STORY_LENGTH:
            raise ValidationError(
                f"custom_story must not exceed {settings.MAX_CUSTOM_STORY_LENGTH} characters (C-5)."
            )

    def save(self, *args, **kwargs):
        """C-2: Enforce max 1,000,000 songs per user."""
        if not self.pk:
            count = type(self).objects.filter(owner=self.owner).count()
            if count >= settings.MAX_SONGS_PER_USER:
                raise ValidationError(
                    f"User library is full. Max {settings.MAX_SONGS_PER_USER} songs allowed (C-2)."
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'"{self.title}" by {self.owner.name}'
