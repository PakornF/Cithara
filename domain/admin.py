"""
Admin registrations for the Cithara domain layer.
Provides CRUD operations for all domain entities via Django Admin (Exercise 3, Task 4).
"""

from django.contrib import admin
from .models import User, Song, MusicGenerationRequest, ShareLink, Feedback


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'has_google', 'has_password', 'created_at', 'last_login_at')
    list_filter = ('created_at',)
    search_fields = ('email', 'name', 'google_id')
    readonly_fields = ('created_at',)

    def has_google(self, obj):
        return bool(obj.google_id)
    has_google.boolean = True
    has_google.short_description = 'Google OAuth'

    def has_password(self, obj):
        return bool(obj.password_hash)
    has_password.boolean = True
    has_password.short_description = 'Manual Login'


class ShareLinkInline(admin.TabularInline):
    model = ShareLink
    extra = 0
    fields = ('token', 'share_url', 'is_active', 'expires_at', 'created_at')
    readonly_fields = ('created_at',)


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    fields = ('user', 'feedback_text', 'is_reviewed', 'submitted_at')
    readonly_fields = ('submitted_at',)


class GenerationRequestInline(admin.TabularInline):
    model = MusicGenerationRequest
    extra = 0
    fields = ('title', 'status', 'is_retry', 'submitted_at')
    readonly_fields = ('submitted_at',)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'genre', 'mood', 'occasion', 'voice_type', 'status', 'creation_date')
    list_filter = ('genre', 'mood', 'occasion', 'voice_type', 'status')
    search_fields = ('title', 'owner__email', 'owner__name')
    readonly_fields = ('creation_date',)
    inlines = [ShareLinkInline, FeedbackInline, GenerationRequestInline]

    fieldsets = (
        ('Core Metadata', {
            'fields': ('owner', 'title', 'genre', 'mood', 'occasion', 'voice_type')
        }),
        ('Content', {
            'fields': ('custom_story', 'prompt_used', 'audio_file_path', 'duration')
        }),
        ('Status', {
            'fields': ('status', 'creation_date')
        }),
    )


@admin.register(MusicGenerationRequest)
class MusicGenerationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'status', 'is_retry', 'submitted_at', 'timed_out_flag')
    list_filter = ('status', 'is_retry', 'genre', 'mood')
    search_fields = ('title', 'user__email', 'user__name')
    readonly_fields = ('submitted_at',)

    fieldsets = (
        ('Request Identity', {
            'fields': ('user', 'song', 'is_retry', 'submitted_at')
        }),
        ('Generation Inputs', {
            'fields': ('title', 'genre', 'mood', 'voice_type', 'occasion', 'custom_story')
        }),
        ('Processing', {
            'fields': ('prompt_generated', 'status', 'error_message')
        }),
    )

    def timed_out_flag(self, obj):
        return obj.is_timed_out()
    timed_out_flag.boolean = True
    timed_out_flag.short_description = 'Timed Out?'


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'song', 'token', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('token', 'song__title')
    readonly_fields = ('created_at',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'song', 'is_reviewed', 'submitted_at')
    list_filter = ('is_reviewed',)
    search_fields = ('user__email', 'feedback_text')
    readonly_fields = ('submitted_at',)
