import os
import shutil
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from articles.models import Article, Comment, Reaction
from users.models import User
from notifications.models import Notification

def clear_cache():
    cache_dir = settings.CACHES['default']['LOCATION']
    if os.path.exists(cache_dir):
        for filename in os.listdir(cache_dir):
            file_path = os.path.join(cache_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

@receiver([post_save, post_delete], sender=Article)
@receiver([post_save, post_delete], sender=Comment)
@receiver([post_save, post_delete], sender=Reaction)
@receiver([post_save, post_delete], sender=User)
@receiver([post_save, post_delete], sender=Notification)
@receiver(post_save, sender=User.following.through)
@receiver(post_delete, sender=User.following.through)
@receiver(post_save, sender=Article.bookmarks.through)
@receiver(post_delete, sender=Article.bookmarks.through)
def clear_cache_on_change(sender, **kwargs):
    clear_cache()