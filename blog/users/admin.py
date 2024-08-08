from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'is_verified', 'is_premium', 'is_staff', 'date_joined', 'is_writer')
    search_fields = ('username', 'email', 'location', 'website')
    list_filter = ('is_verified', 'is_premium', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'profile_picture', 'location', 'website', 'following', 'blocked_users', 'is_verified', 'is_premium')}),
    )
    readonly_fields = ('date_joined',)
