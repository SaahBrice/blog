from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SiteSettings
from django.utils.html import format_html


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_verified', 'is_premium', 'is_staff', 'date_joined', 'is_manual_writer', 'avatar_preview')
    search_fields = ('username', 'email', 'location', 'website')
    list_filter = ('is_verified', 'is_premium', 'is_staff', 'is_superuser', 'is_active','is_manual_writer', 'date_joined')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'profile_picture', 'location', 'website', 'following', 'blocked_users', 'is_verified', 'is_premium','is_manual_writer')}),
    )
    readonly_fields = ('date_joined',)

    def avatar_preview(self, obj):
        return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.get_avatar_url())

    avatar_preview.short_description = 'Avatar'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'min_articles_for_writer', 'min_followers_for_writer', 'min_reactions_for_writer','min_articles_for_suggestions', 'max_suggested_users')



    fieldsets = (
        ('General Settings', {
            'fields': ('site_name', 'site_logo'),
        }),
        ('Writer Criteria', {
            'fields': ('min_articles_for_writer', 'min_followers_for_writer', 'min_reactions_for_writer', 'min_articles_for_suggestions', 'max_suggested_users'),
        }),
        # Add more fieldsets as needed for future settings
    )

    def has_add_permission(self, request):
        # Prevent creating multiple instances
        return SiteSettings.objects.count() == 0

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting the settings instance
        return False

    def get_actions(self, request):
        # Remove delete action from dropdown
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions