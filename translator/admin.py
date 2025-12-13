from django.contrib import admin
from .models import Translation


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ['share_slug', 'mode', 'view_count', 'created_at']
    list_filter = ['mode', 'created_at']
    search_fields = ['original_text', 'translated_text', 'share_slug']
    readonly_fields = ['id', 'share_slug', 'created_at']
    date_hierarchy = 'created_at'
