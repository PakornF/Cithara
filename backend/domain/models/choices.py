from django.db import models


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
    Pending -> InProgress -> Completed | Failed | TimedOut | Rejected
    """

    PENDING = 'Pending', 'Pending'
    INPROGRESS = 'InProgress', 'In Progress'
    COMPLETED = 'Completed', 'Completed'
    FAILED = 'Failed', 'Failed'
    TIMEDOUT = 'TimedOut', 'Timed Out'
    REJECTED = 'Rejected', 'Rejected'
