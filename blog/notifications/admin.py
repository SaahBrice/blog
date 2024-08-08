from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'article', 'comment', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'text')
    list_filter = ('notification_type', 'is_read', 'created_at')
    raw_id_fields = ('recipient', 'sender', 'article', 'comment')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        # Custom queryset to select related fields for performance optimization
        return super().get_queryset(request).select_related('recipient', 'sender', 'article', 'comment')
