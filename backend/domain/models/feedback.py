from django.db import models


class Feedback(models.Model):
    """User-submitted feedback on a generated song (FR-50)."""

    user = models.ForeignKey(
        'domain.User',
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    song = models.ForeignKey(
        'domain.Song',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        help_text='Optional – feedback may not reference a specific song.',
    )
    feedback_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(
        default=False,
        help_text='Internal flag for TA/admin review.',
    )

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-submitted_at']

    def __str__(self):
        song_label = f' on Song#{self.song_id}' if self.song_id else ''
        return f'Feedback#{self.pk} by {self.user.name}{song_label}'
