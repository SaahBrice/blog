from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    language = models.CharField(max_length=2, choices=[('EN', 'English'), ('FR', 'French')])
    tags = TaggableManager()
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_articles', blank=True)


    @classmethod
    def get_recent_articles_for_user(cls, user, limit=10):
        return cls.objects.filter(
            author__in=user.following.all(),
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:limit]
    
    def is_bookmarked_by(self, user):
        return self.bookmarks.filter(id=user.id).exists()

    @classmethod
    def get_recommended_articles(cls, user, limit=5):
        # Get the tags of articles the user has interacted with
        user_tags = cls.objects.filter(bookmarks=user).values_list('tags__name', flat=True)
        
        # Find articles with similar tags, excluding user's own articles and already bookmarked ones
        recommended = cls.objects.filter(tags__name__in=user_tags, status='published')\
            .exclude(author=user)\
            .exclude(bookmarks=user)\
            .distinct()
        
        # If not enough recommendations, add some recent articles
        if recommended.count() < limit:
            recent = cls.objects.filter(status='published')\
                .exclude(author=user)\
                .exclude(bookmarks=user)\
                .order_by('-published_at')
            recommended = (list(recommended) + list(recent))[:limit]
        
        return recommended[:limit]

    @property
    def clap_count(self):
        return self.reactions.filter(reaction_type='clap').count()

    @property
    def sad_count(self):
        return self.reactions.filter(reaction_type='sad').count()

    @property
    def laugh_count(self):
        return self.reactions.filter(reaction_type='laugh').count()


    def __str__(self):
        return self.title


class Reaction(models.Model):
    REACTION_TYPES = (
        ('clap', 'Clap'),
        ('sad', 'Sad'),
        ('laugh', 'Laugh'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=5, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article', 'reaction_type')







class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'