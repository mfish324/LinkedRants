from django.db import models
from django.urls import reverse
from django.utils.text import slugify
import uuid
import markdown
import bleach


class Category(models.Model):
    """Predefined categories for rants."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, blank=True)  # emoji
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('rants:category', kwargs={'slug': self.slug})


class Rant(models.Model):
    """Main rant/post submission."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='rants')
    is_anonymous = models.BooleanField(default=True)
    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, help_text="Optional, for notifications if featured")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)  # for moderation
    is_featured = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Rant {self.id}"

    def get_absolute_url(self):
        return reverse('rants:detail', kwargs={'pk': self.id})

    @property
    def author_display(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.display_name or "Anonymous"

    @property
    def body_html(self):
        """Render markdown body to safe HTML."""
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'blockquote',
            'code', 'pre', 'h1', 'h2', 'h3', 'a'
        ]
        allowed_attrs = {'a': ['href', 'title']}
        html = markdown.markdown(self.body, extensions=['fenced_code'])
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)

    def get_reaction_counts(self):
        """Get counts for each reaction type."""
        counts = {}
        for code, emoji in Reaction.REACTION_TYPES:
            counts[code] = self.reactions.filter(reaction_type=code).count()
        return counts

    @property
    def total_reactions(self):
        return self.reactions.count()


class SideBySide(models.Model):
    """LinkedIn vs Reality comparison submission."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    linkedin_version = models.TextField(help_text="The LinkedIn version (cringe)")
    reality_version = models.TextField(help_text="The reality (what actually happened)")
    context = models.CharField(max_length=200, blank=True, help_text="Brief setup/context")
    is_anonymous = models.BooleanField(default=True)
    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Side by Side"
        verbose_name_plural = "Side by Sides"
        ordering = ['-created_at']

    def __str__(self):
        return self.context or f"SideBySide {self.id}"

    def get_absolute_url(self):
        return reverse('rants:sidebyside_detail', kwargs={'pk': self.id})

    @property
    def author_display(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.display_name or "Anonymous"

    def get_reaction_counts(self):
        """Get counts for each reaction type."""
        counts = {}
        for code, emoji in Reaction.REACTION_TYPES:
            counts[code] = self.reactions.filter(reaction_type=code).count()
        return counts

    @property
    def total_reactions(self):
        return self.reactions.count()


class GhostingStory(models.Model):
    """Wall of Shame - recruiter ghosting stories."""
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('indeed', 'Indeed'),
        ('other', 'Other'),
    ]

    STAGE_CHOICES = [
        ('applied', 'Just Applied'),
        ('screening', 'Phone Screen'),
        ('interview', 'After Interview(s)'),
        ('final', 'Final Round'),
        ('offer', 'Verbal Offer Stage'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recruiter_name = models.CharField(max_length=200, blank=True, help_text="Recruiter's name (optional)")
    company = models.CharField(max_length=200)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='linkedin')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='applied')
    story = models.TextField(help_text="What happened? How did they ghost you?")
    is_anonymous = models.BooleanField(default=True)
    display_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Ghosting Story"
        verbose_name_plural = "Ghosting Stories"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company} - {self.get_stage_display()}"

    def get_absolute_url(self):
        return reverse('rants:ghosting_detail', kwargs={'pk': self.id})

    @property
    def author_display(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.display_name or "Anonymous"

    @property
    def story_html(self):
        """Render markdown body to safe HTML."""
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'blockquote',
            'code', 'pre', 'h1', 'h2', 'h3', 'a'
        ]
        allowed_attrs = {'a': ['href', 'title']}
        html = markdown.markdown(self.story, extensions=['fenced_code'])
        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)

    def get_reaction_counts(self):
        """Get counts for each reaction type."""
        counts = {}
        for code, emoji in Reaction.REACTION_TYPES:
            counts[code] = self.reactions.filter(reaction_type=code).count()
        return counts

    @property
    def total_reactions(self):
        return self.reactions.count()


class Reaction(models.Model):
    """Anti-LinkedIn reactions for rants and side-by-sides."""
    REACTION_TYPES = [
        ('drink', '🍷'),   # "This is why I drink"
        ('dead', '💀'),    # "Dead inside"
        ('felt', '🤝'),    # "Felt that"
        ('rage', '😤'),    # "Rage"
        ('peak', '🎭'),    # "Peak LinkedIn"
        ('clap', '👏'),    # "Slow clap"
    ]

    REACTION_LABELS = {
        'drink': 'This is why I drink',
        'dead': 'Dead inside',
        'felt': 'Felt that',
        'rage': 'Rage',
        'peak': 'Peak LinkedIn',
        'clap': 'Slow clap',
    }

    rant = models.ForeignKey(
        Rant, on_delete=models.CASCADE,
        related_name='reactions', null=True, blank=True
    )
    sidebyside = models.ForeignKey(
        SideBySide, on_delete=models.CASCADE,
        related_name='reactions', null=True, blank=True
    )
    ghosting_story = models.ForeignKey(
        GhostingStory, on_delete=models.CASCADE,
        related_name='reactions', null=True, blank=True
    )
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    session_key = models.CharField(max_length=100)  # prevent duplicates
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One reaction per session per content item
        constraints = [
            models.UniqueConstraint(
                fields=['rant', 'session_key', 'reaction_type'],
                name='unique_rant_reaction'
            ),
            models.UniqueConstraint(
                fields=['sidebyside', 'session_key', 'reaction_type'],
                name='unique_sidebyside_reaction'
            ),
            models.UniqueConstraint(
                fields=['ghosting_story', 'session_key', 'reaction_type'],
                name='unique_ghosting_reaction'
            ),
        ]

    def __str__(self):
        return f"{self.get_reaction_type_display()} on {self.rant or self.sidebyside or self.ghosting_story}"

    @classmethod
    def get_emoji(cls, code):
        return dict(cls.REACTION_TYPES).get(code, '')

    @classmethod
    def get_label(cls, code):
        return cls.REACTION_LABELS.get(code, '')
