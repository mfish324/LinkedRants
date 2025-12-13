from django.contrib import admin
from .models import Category, Rant, SideBySide, Reaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Rant)
class RantAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_anonymous', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['category', 'is_approved', 'is_featured', 'is_reported', 'created_at']
    search_fields = ['title', 'body', 'display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
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
    list_display = ['context', 'is_anonymous', 'is_approved', 'is_featured', 'created_at']
    list_filter = ['is_approved', 'is_featured', 'is_reported', 'created_at']
    search_fields = ['context', 'linkedin_version', 'reality_version', 'display_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ['reaction_type', 'rant', 'sidebyside', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    readonly_fields = ['created_at']
