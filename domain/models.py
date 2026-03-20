"""
Domain Layer – Cithara
======================
Implements the domain model defined in Exercise 2.
All entities, relationships, constraints and enumerations are derived
directly from the SRS (v1.0) and the UML domain model.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone


# ---------------------------------------------------------------------------
# Enumerations  (FR-09, FR-10, FR-11, FR-12)
# ---------------------------------------------------------------------------

class Genre(models.TextChoices):
    """Fixed set of music genres selectable during generation (FR-09)."""
    POP = 'Pop', 'Pop'
    ROCK = 'Rock', 'Rock'
    JAZZ = 'Jazz', 'Jazz'
    CLASSICAL = 'Classical', 'Classical'
    HIPHOP = 'Hiphop', 'Hiphop'


class Mood(models.TextChoices):
    """Fixed set of emotional tones (FR-10)."""
    HAPPY = 'Happy', 'Happy'
    SAD = 'Sad', 'Sad'
    ROMANTIC = 'Romantic', 'Romantic'
    ENERGETIC = 'Energetic', 'Energetic'
    CALM = 'Calm', 'Calm'


class Occasion(models.TextChoices):
    """Fixed set of event contexts (FR-12)."""
    BIRTHDAY = 'Birthday', 'Birthday'
    WEDDING = 'Wedding', 'Wedding'
    GRADUATION = 'Graduation', 'Graduation'
    ANNIVERSARY = 'Anniversary', 'Anniversary'
    CUSTOM = 'Custom', 'Custom'


class VoiceType(models.TextChoices):
    """Binary voice option (FR-11, US-06)."""
    MALE = 'Male', 'Male'
    FEMALE = 'Female', 'Female'


class GenerationStatus(models.TextChoices):
    """
    Lifecycle states of a generation request (FR-16, FR-17, FR-18).
    Pending → InProgress → Completed | Failed | TimedOut | Rejected
    """
    PENDING = 'Pending', 'Pending'
    INPROGRESS = 'InProgress', 'In Progress'
    COMPLETED = 'Completed', 'Completed'
    FAILED = 'Failed', 'Failed'
    TIMEDOUT = 'TimedOut', 'Timed Out'
    REJECTED = 'Rejected', 'Rejected'


# ---------------------------------------------------------------------------
# User  (FR-01 – FR-07, C-3)
# ---------------------------------------------------------------------------

class User(models.Model):
    """
    Represents an authenticated person using Cithara.
    Supports dual authentication: Google OAuth (googleId) and manual login
    (passwordHash). At least one must be present (C-3).

    Two roles exist in the SRS: Creator and Listener. Both are the same
    entity – role is determined by behaviour (what the user does), not by a
    stored flag, consistent with the domain model.
    """
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True,
                                     help_text="Populated for Google OAuth users (FR-01).")
    password_hash = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="Populated for manual-login users (FR-02).")
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


# ---------------------------------------------------------------------------
# Song  (FR-17, FR-28 – FR-35, C-1, C-2, C-7)
# ---------------------------------------------------------------------------

class Song(models.Model):
    """
    Central domain entity. Represents an AI-generated audio piece.
    Lifecycle: generated → previewed → (optionally) saved.

    audioFilePath and duration are optional because they are only populated
    once GenerationStatus reaches Completed (C-7).
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='songs',
        help_text="C-1: A Song belongs to exactly one User.",
    )
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=50, choices=Genre.choices)
    mood = models.CharField(max_length=50, choices=Mood.choices)
    occasion = models.CharField(max_length=50, choices=Occasion.choices)
    voice_type = models.CharField(max_length=10, choices=VoiceType.choices)
    custom_story = models.TextField(
        blank=True, null=True,
        help_text="Optional (FR-13). Max 1,000 characters (C-5).",
    )
    prompt_used = models.TextField(
        blank=True, null=True,
        help_text="Stored on Song for display without joining back to request (US-17).",
    )
    audio_file_path = models.CharField(
        max_length=1024, blank=True, null=True,
        help_text="C-7: Only populated when GenerationStatus = Completed.",
    )
    duration = models.IntegerField(
        null=True, blank=True,
        help_text="Duration in seconds. Only populated after successful generation (C-7).",
    )
    status = models.CharField(
        max_length=20, choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
    )
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
        ordering = ['-creation_date']   # FR-32: newest first

    def clean(self):
        """C-5: customStory must not exceed 1,000 characters."""
        if self.custom_story and len(self.custom_story) > settings.MAX_CUSTOM_STORY_LENGTH:
            raise ValidationError(
                f"custom_story must not exceed {settings.MAX_CUSTOM_STORY_LENGTH} characters (C-5)."
            )

    def save(self, *args, **kwargs):
        """C-2: Enforce max 1,000,000 songs per user."""
        if not self.pk:  # only on creation
            count = Song.objects.filter(owner=self.owner).count()
            if count >= settings.MAX_SONGS_PER_USER:
                raise ValidationError(
                    f"User library is full. Max {settings.MAX_SONGS_PER_USER} songs allowed (C-2)."
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'"{self.title}" by {self.owner.name}'


# ---------------------------------------------------------------------------
# MusicGenerationRequest  (FR-08 – FR-18, FR-24 – FR-27, C-4, C-5, C-9, C-10)
# ---------------------------------------------------------------------------

class MusicGenerationRequest(models.Model):
    """
    Captures structured inputs for a song generation job.
    Preserved on failure to support retry without re-entering inputs (Assumption 6).
    isRetry defaults to False and is set True on regeneration (FR-24).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='generation_requests',
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='generation_requests',
        help_text="Populated once a Song is successfully produced (0..* → 0..1).",
    )

    # --- Generation inputs ---
    title = models.CharField(max_length=255, help_text="C-4: Mandatory.")
    genre = models.CharField(max_length=50, choices=Genre.choices)
    mood = models.CharField(max_length=50, choices=Mood.choices)
    voice_type = models.CharField(max_length=10, choices=VoiceType.choices)
    occasion = models.CharField(max_length=50, choices=Occasion.choices)
    custom_story = models.TextField(
        blank=True, null=True,
        help_text="Optional (FR-13). Max 1,000 characters (C-5).",
    )

    # --- State ---
    prompt_generated = models.TextField(
        blank=True, null=True,
        help_text="The prompt constructed and sent to Suno AI (FR-17).",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_retry = models.BooleanField(
        default=False,
        help_text="True when this is a regeneration attempt (FR-24).",
    )
    status = models.CharField(
        max_length=20, choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
    )
    error_message = models.TextField(
        blank=True, null=True,
        help_text="Populated only on failure/timeout/rejection. Null on success (FR-18, FR-49).",
    )

    class Meta:
        verbose_name = 'Music Generation Request'
        verbose_name_plural = 'Music Generation Requests'
        ordering = ['-submitted_at']

    def clean(self):
        """C-4 + C-5 validation."""
        if not self.title or not self.title.strip():
            raise ValidationError("Title is mandatory before submitting a generation request (C-4).")
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
        return f"Request#{self.pk}{retry_label} – '{self.title}' ({self.status})"


# ---------------------------------------------------------------------------
# ShareLink  (FR-36 – FR-41, C-6, C-8)
# ---------------------------------------------------------------------------

class ShareLink(models.Model):
    """
    Secure tokenized URL for sharing a saved Song (FR-37).
    Composition under Song: cannot exist without its parent.
    Deleting a Song cascades and removes the ShareLink (C-8).
    isActive defaults to True; set False when the song is deleted (FR-41).
    expiresAt is retained for future link-expiry support (Open Issue 5).
    """
    song = models.OneToOneField(
        Song,
        on_delete=models.CASCADE,
        related_name='share_link',
        help_text="C-8: Composition – ShareLink is deleted with its Song.",
    )
    token = models.CharField(max_length=255, unique=True)
    share_url = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Reserved for future link-expiry (Open Issue 5). Currently null (Assumption 5).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Set False when the parent Song is deleted (FR-41).",
    )

    class Meta:
        verbose_name = 'Share Link'
        verbose_name_plural = 'Share Links'

    def __str__(self):
        return f"ShareLink for Song#{self.song_id} – active={self.is_active}"


# ---------------------------------------------------------------------------
# Feedback  (FR-50, FR-51, C-14)
# ---------------------------------------------------------------------------

class Feedback(models.Model):
    """
    User-submitted feedback on a generated song (FR-50).
    Stored for internal analysis; never exposed publicly (C-14, NFR-41).
    The Song FK is optional because feedback may be general (Key Modelling Assumption).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    song = models.ForeignKey(
        Song,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='feedbacks',
        help_text="Optional – feedback may not reference a specific song.",
    )
    feedback_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(
        default=False,
        help_text="Internal flag for TA/admin review.",
    )

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-submitted_at']

    def __str__(self):
        song_label = f' on Song#{self.song_id}' if self.song_id else ''
        return f"Feedback#{self.pk} by {self.user.name}{song_label}"
