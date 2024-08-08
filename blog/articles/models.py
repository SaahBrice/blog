from django.db import models
from django.conf import settings
from django.forms import ValidationError
from taggit.managers import TaggableManager
from django.utils import timezone
import json

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

    def get_content_as_html(self):
        try:
            content_json = json.loads(self.content)
            html = ""
            for block in content_json['blocks']:
                if block['type'] == 'header':
                    html += f"<h{block['data']['level']}>{block['data']['text']}</h{block['data']['level']}>"
                elif block['type'] == 'paragraph':
                    html += f"<p>{block['data']['text']}</p>"
                elif block['type'] == 'list':
                    list_type = 'ol' if block['data']['style'] == 'ordered' else 'ul'
                    html += f"<{list_type}>"
                    for item in block['data']['items']:
                        html += f"<li>{item}</li>"
                    html += f"</{list_type}>"
            return html
        except json.JSONDecodeError:
            return self.content
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
        
    def reaction_count(self, reaction_type):
        return self.reactions.filter(reaction_type=reaction_type).aggregate(total=models.Sum('count'))['total'] or 0

    @property
    def clap_count(self):
        return self.reaction_count('clap')

    @property
    def sad_count(self):
        return self.reaction_count('sad')

    @property
    def laugh_count(self):
        return self.reaction_count('laugh')

    @property
    def total_reactions(self):
        return self.reactions.aggregate(total=models.Sum('count'))['total'] or 0

    @property
    def comment_count(self):
        return self.comments.count()




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
    count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'article', 'reaction_type')

    def clean(self):
        if self.count > 100:
            raise ValidationError("You can't react more than 100 times to an article.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)




class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    mentioned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Mention', related_name='mentioned_in')

    @property
    def clap_count(self):
        return self.reactions.filter(reaction_type='clap').aggregate(total=models.Sum('count'))['total'] or 0

    @property
    def laugh_count(self):
        return self.reactions.filter(reaction_type='laugh').aggregate(total=models.Sum('count'))['total'] or 0

    @property
    def sad_count(self):
        return self.reactions.filter(reaction_type='sad').aggregate(total=models.Sum('count'))['total'] or 0

    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'
        

class CommentReaction(models.Model):
    REACTION_TYPES = (
        ('clap', 'Clap'),
        ('laugh', 'Laugh'),
        ('sad', 'Sad'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=5, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    count = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.count > 100:
            raise ValidationError("You can't react more than 100 times to a comment.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    class Meta:
        unique_together = ('user', 'comment', 'reaction_type')



class Mention(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentions')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='mentions')
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('comment', 'position')