from django.contrib import admin
from .models import Category, Rant, SideBySide, GhostingStory, Reaction, ContentView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Rant)
class RantAdmin(admin.ModelAdmin):
    list_display = ['title', 'share_slug', 'category', 'is_anonymous', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['category', 'is_approved', 'is_featured', 'is_reported', 'created_at']
    search_fields = ['title', 'body', 'display_name', 'share_slug']
    readonly_fields = ['id', 'share_slug', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['approve_rants', 'feature_rants', 'unflag_rants']

    @admin.action(description="Approve selected rants")
    def approve_rants(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Feature selected rants")
    def feature_rants(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Clear reports on selected rants")
    def unflag_rants(self, request, queryset):
        queryset.update(is_reported=False, report_count=0)


@admin.register(SideBySide)
class SideBySideAdmin(admin.ModelAdmin):
    list_display = ['context', 'share_slug', 'is_anonymous', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['is_approved', 'is_featured', 'is_reported', 'created_at']
    search_fields = ['context', 'linkedin_version', 'reality_version', 'display_name', 'share_slug']
    readonly_fields = ['id', 'share_slug', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(GhostingStory)
class GhostingStoryAdmin(admin.ModelAdmin):
    list_display = ['company', 'recruiter_name', 'platform', 'stage', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['platform', 'stage', 'is_approved', 'is_featured', 'is_reported', 'created_at']
    search_fields = ['company', 'recruiter_name', 'story', 'display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['approve_stories', 'feature_stories', 'unflag_stories']

    @admin.action(description="Approve selected stories")
    def approve_stories(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Feature selected stories")
    def feature_stories(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Clear reports on selected stories")
    def unflag_stories(self, request, queryset):
        queryset.update(is_reported=False, report_count=0)


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['reaction_type', 'rant', 'sidebyside', 'ghosting_story', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ContentView)
class ContentViewAdmin(admin.ModelAdmin):
    list_display = ['get_content', 'referrer', 'timestamp']
    list_filter = ['referrer', 'timestamp']
    readonly_fields = ['rant', 'sidebyside', 'ghosting_story', 'referrer', 'timestamp']
    date_hierarchy = 'timestamp'

    def get_content(self, obj):
        if obj.rant:
            return f"Rant: {obj.rant.share_slug}"
        elif obj.sidebyside:
            return f"SideBySide: {obj.sidebyside.share_slug}"
        elif obj.ghosting_story:
            return f"Ghosting: {obj.ghosting_story.company}"
        return "Unknown"
    get_content.short_description = 'Content'
