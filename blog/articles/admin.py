from django.contrib import admin

from .models import Article, Reaction, Comment, CommentReaction, Mention

# Register the Article model with custom admin settings
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at', 'created_at')
    search_fields = ('title', 'author__username', 'tags__name')
    list_filter = ('status', 'language', 'created_at', 'published_at')
    prepopulated_fields = {"title": ("title",)}  # Automatically generates slug if needed
    raw_id_fields = ('author',)
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)

# Register the Reaction model
@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'reaction_type', 'count', 'created_at')
    search_fields = ('user__username', 'article__title')
    list_filter = ('reaction_type', 'created_at')
    raw_id_fields = ('user', 'article')
    ordering = ('-created_at',)

# Register the Comment model with inline support for CommentReaction
class CommentReactionInline(admin.TabularInline):
    model = CommentReaction
    extra = 1

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'content', 'created_at')
    search_fields = ('author__username', 'article__title', 'content')
    list_filter = ('created_at',)
    raw_id_fields = ('author', 'article', 'parent')
    inlines = [CommentReactionInline]
    ordering = ('-created_at',)

# Register the CommentReaction model
@admin.register(CommentReaction)
class CommentReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'reaction_type', 'count', 'created_at')
    search_fields = ('user__username', 'comment__content')
    list_filter = ('reaction_type', 'created_at')
    raw_id_fields = ('user', 'comment')
    ordering = ('-created_at',)

# Register the Mention model
@admin.register(Mention)
class MentionAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'position')
    search_fields = ('user__username', 'comment__content')
    raw_id_fields = ('user', 'comment')
