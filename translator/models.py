from django.db import models
from django.urls import reverse
import uuid


class Translation(models.Model):
    """Saved translations from the LinkedIn Translator tool."""
    MODE_CHOICES = [
        ('to_linkedin', 'Make it LinkedIn'),
        ('to_reality', 'Make it Real'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_text = models.TextField()
    translated_text = models.TextField()
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    share_slug = models.SlugField(unique=True, max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        mode_display = "LinkedIn" if self.mode == 'to_linkedin' else "Reality"
        return f"Translation to {mode_display} ({self.share_slug})"

    def get_absolute_url(self):
        return reverse('translator:share', kwargs={'slug': self.share_slug})

    def save(self, *args, **kwargs):
        if not self.share_slug:
            # Generate a short random slug
            import secrets
            self.share_slug = secrets.token_urlsafe(8)[:12]
        super().save(*args, **kwargs)
