from django.db import models
from django.conf import settings
from django.forms import ValidationError
from taggit.managers import TaggableManager
from django.utils import timezone
import json
from django.utils.safestring import mark_safe
from django.utils.html import escape
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import logging
import sys


logger = logging.getLogger(__name__)


def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 10 MB
        raise ValidationError("The maximum file size that can be uploaded is 10 MB")



class Article(models.Model):
    title = models.CharField(max_length=70)
    content = models.TextField()
    image = models.ImageField(upload_to='article_images/', validators=[validate_file_size], null=True, blank=True)
    thumbnail = models.ImageField(upload_to='article_thumbnails/', validators=[validate_file_size], null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')
    language = models.CharField(max_length=2, choices=[('EN', 'English'), ('FR', 'French')])
    tags = TaggableManager()
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_articles', blank=True)

    def compress_image(self):
        if not self.thumbnail:
            return

        try:
            img = Image.open(self.thumbnail)
            
            if img.format.lower() not in ['jpeg', 'jpg', 'png', 'gif']:
                raise ValueError(f"Unsupported image format: {img.format}")

            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            output = BytesIO()
            
            # Attempt to compress the image
            img.save(output, format='JPEG', quality=30)  # Compress by 70%
            output.seek(0)
            
            # Check if compression actually reduced file size
            if output.getbuffer().nbytes >= self.thumbnail.size:
                logger.warning(f"Compression did not reduce file size for {self.thumbnail.name}")
                return  # Skip compression if it didn't reduce file size
            
            self.thumbnail = InMemoryUploadedFile(
                output,
                'ImageField',
                f"{self.thumbnail.name.split('.')[0]}.jpg",
                'image/jpeg',
                output.getbuffer().nbytes,
                None
            )
        except IOError as e:
            logger.error(f"IOError while compressing image: {str(e)}")
            raise ValidationError("Error occurred while processing the image. Please try again.")
        except ValueError as e:
            logger.error(f"ValueError while compressing image: {str(e)}")
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(f"Unexpected error while compressing image: {str(e)}")
            raise ValidationError("An unexpected error occurred while processing the image. Please try again.")

    def save(self, *args, **kwargs):
        if self.pk is None:  # New instance
            super().save(*args, **kwargs)
            try:
                self.compress_image()
            except ValidationError as e:
                # If compression fails, we still want to save the original image
                logger.warning(f"Image compression failed, saving original: {str(e)}")
        super().save(*args, **kwargs)

    def get_content_as_html(self):
        try:
            content_json = json.loads(self.content)
        except json.JSONDecodeError:
            return mark_safe("<p>Error: Could not parse content</p>")

        if not isinstance(content_json, dict) or 'blocks' not in content_json:
            return mark_safe("<p>Error: Invalid content structure</p>")

        html = ""
        for block in content_json['blocks']:
            block_type = block.get('type')
            block_data = block.get('data', {})

            if block_type == 'header':
                level = block_data.get('level', 1)
                text = block_data.get('text', '')
                html += f"<h{level}>{text}</h{level}>"
            elif block_type == 'paragraph':
                text = block_data.get('text', '')
                html += f"<p>{text}</p>"
            elif block_type in ['image', 'SimpleImage']:
                url = block_data.get('file', {}).get('url') or block_data.get('url', '')
                caption = block_data.get('caption', '')
                html += f'<figure><img src="{url}" alt="{caption}">'
                if caption:
                    html += f'<figcaption>{caption}</figcaption>'
                html += '</figure>'
            elif block_type == 'list':
                style = block_data.get('style', 'unordered')
                items = block_data.get('items', [])
                list_tag = 'ul' if style == 'unordered' else 'ol'
                html += f"<{list_tag}>"
                for item in items:
                    html += f"<li>{item}</li>"
                html += f"</{list_tag}>"
            elif block_type == 'quote':
                text = block_data.get('text', '')
                caption = block_data.get('caption', '')
                html += f'<blockquote>{text}'
                if caption:
                    html += f'<footer>{caption}</footer>'
                html += '</blockquote>'
            elif block_type == 'code':
                code = block_data.get('code', '')
                escaped_code = escape(code)
                html += f'<pre><code>{escaped_code}</code></pre>'
            elif block_type == 'table':
                html += '<table>'
                for row in block_data.get('content', []):
                    html += '<tr>'
                    for cell in row:
                        html += f'<td>{cell}</td>'
                    html += '</tr>'
                html += '</table>'
            elif block_type == 'embed':
                service = block_data.get('service', '')
                source = block_data.get('source', '')
                embed = block_data.get('embed', '')
                caption = block_data.get('caption', '')
                if service == 'youtube' and embed:
                    html += f'<figure class="embed"><iframe width="560" height="315" src="{embed}" frameborder="0" allowfullscreen></iframe>'
                    if caption:
                        html += f'<figcaption>{caption}</figcaption>'
                    html += '</figure>'
                else:
                    html += f'<a href="{source}" target="_blank">{caption or source}</a>'
            else:
                html += f"<p>Unsupported block type: {block_type}</p>"

        return mark_safe(html)


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