
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Mention, Article, Comment, Reaction, CommentReaction
from .forms import ArticleForm, CommentForm
from taggit.models import Tag
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from users.models import User
from users.services import toggle_follow
from notifications.services import create_notification
from django.db import transaction
from django.db.models import Count
import re
from django.db.models import Q
from django.template.loader import render_to_string
from django.db import connection
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from uuid import uuid4
import os
from django.views.generic import TemplateView
from users.services import get_suggested_users









class WelcomeView(TemplateView):
    template_name = 'welcome.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('article_list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_articles'] = Article.objects.filter(status='published').order_by('-published_at')[:5]
        return context


class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(status='published').order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # New articles
            context['new_articles'] = Article.objects.filter(status='published').order_by('-published_at')[:5]
            
            # Articles from followees
            followee_articles = Article.objects.filter(
                author__in=user.following.all(),
                status='published'
            ).annotate(interaction_count=Count('reactions') + Count('comments')).order_by('-interaction_count')[:5]
            context['followee_articles'] = followee_articles
            
            # Discover articles
            user_tags = Article.objects.filter(reactions__user=user).values_list('tags__name', flat=True).distinct()
            discover_articles = Article.objects.filter(status='published').exclude(
                tags__name__in=user_tags
            ).order_by('?')[:5]
            context['discover_articles'] = discover_articles
            context['tags']=Tag.objects.all()
            context['suggested_users'] = get_suggested_users(user)
        return context



class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_following'] = self.request.user.following.filter(id=self.object.author.id).exists()
            context['is_bookmarked'] = self.object.bookmarks.filter(id=self.request.user.id).exists()
            context['comment_form'] = CommentForm()
            context['user_reactions'] = Reaction.objects.filter(user=self.request.user,article=self.object).values_list('reaction_type', flat=True)
        return context

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        with transaction.atomic():
            article = get_object_or_404(Article, pk=self.kwargs['pk'])
            form.instance.article = article
            form.instance.author = self.request.user
            comment = form.save()
            process_mentions(comment,self.request.user)
            # Create notification for the article author
            create_notification(
                recipient=article.author,
                notification_type='comment',
                sender=self.request.user,
                article=article,
                comment=comment
            )
        comment_html = render_to_string('articles/comment.html', {'comment': comment}, request=self.request)

        # Apply render_mentions filter to the rendered HTML
        #comment_html = Template("{% load comment_tags %}" + comment_html).render(Context({'comment': comment}))

        return JsonResponse({
            'success': True,
            'comment_html': comment_html,
            'comment_count': article.comment_count
        })

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'error': form.errors})


    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.kwargs['pk']})






class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('article_detail', kwargs={'pk': self.object.pk})
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'error': form.errors
        })

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('article_list')

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('article_detail', kwargs={'pk': self.object.pk})
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'error': form.errors
        })

class ArticlesByTagView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(tags__slug=self.kwargs['tag_slug'], status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['current_tag'] = self.kwargs['tag_slug']
        return context
    


class ActivityFeedView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'users/activity_feed.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return Article.get_recent_articles_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.is_ajax():
            context['template'] = 'users/activity_feed_articles.html'
        return context

@login_required
@require_POST
def toggle_bookmark(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.is_bookmarked_by(request.user):
        article.bookmarks.remove(request.user)
        bookmarked = False
    else:
        article.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})

@login_required
@require_POST
def toggle_follow_author(request, author_id):
    author = get_object_or_404(User, id=author_id)
    is_following = toggle_follow(request.user, author)
    return JsonResponse({'is_following': is_following})



@login_required
@require_POST
def toggle_reaction(request, pk):
    article = get_object_or_404(Article, pk=pk)
    reaction_type = request.POST.get('reaction_type')
    amount = int(request.POST.get('amount', 1))

    if reaction_type not in dict(Reaction.REACTION_TYPES):
        return JsonResponse({'error': 'Invalid reaction type'}, status=400)

    if amount not in [10, 50, 100]:
        return JsonResponse({'error': 'Invalid reaction amount'}, status=400)

    with transaction.atomic():
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            article=article,
            reaction_type=reaction_type,
            defaults={'count': 0}
        )

        new_count = min(reaction.count + amount, 100)
        reaction.count = new_count
        reaction.save()

    create_notification(article.author, reaction_type, sender=request.user, article=article)

    return JsonResponse({
        'clap_count': article.clap_count,
        'sad_count': article.sad_count,
        'laugh_count': article.laugh_count,
    })





class BookmarkedArticlesView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'articles/bookmarked_articles.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return self.request.user.bookmarked_articles.all()

@login_required
def remove_bookmark(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.bookmarks.remove(request.user)
    return redirect('bookmarked_articles')

@login_required
@require_POST
def toggle_comment_reaction(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    reaction_type = request.POST.get('reaction_type')
    amount = int(request.POST.get('amount', 10))  # Default to 10 if not provided

    if reaction_type not in dict(CommentReaction.REACTION_TYPES):
        return JsonResponse({'error': 'Invalid reaction type'}, status=400)

    if amount not in [10, 50, 100]:
        return JsonResponse({'error': 'Invalid reaction amount'}, status=400)

    with transaction.atomic():
        reaction, created = CommentReaction.objects.get_or_create(
            user=request.user,
            comment=comment,
            reaction_type=reaction_type,
            defaults={'count': 0}
        )

        new_count = min(reaction.count + amount, 100)
        reaction.count = new_count
        reaction.save()

        # Update article's clap reaction count
        article = comment.article
        article_reaction, _ = Reaction.objects.get_or_create(
            user=request.user,
            article=article,
            reaction_type='clap'
        )
        article_reaction.count = min(article_reaction.count + amount, 100)
        article_reaction.save()


        # Notify the comment author
        create_notification(
            recipient=comment.author,
            notification_type='comment_reaction',
            sender=request.user,
            article=article,
            comment=comment
        )

    return JsonResponse({
        'comment_id':comment.id,
        'clap_count': comment.clap_count,
        'laugh_count': comment.laugh_count,
        'sad_count': comment.sad_count,
        'article_clap_count': article.clap_count
    })



@login_required
@require_POST
def add_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        with transaction.atomic():
            reply = Comment.objects.create(
                article=parent_comment.article,
                author=request.user,
                content=content,
                parent=parent_comment
            )
            process_mentions(reply, request.user)
        
        # Notify the parent comment author
        create_notification(
            recipient=parent_comment.author,
            notification_type='reply',
            sender=request.user,
            article=parent_comment.article,
            comment=reply
        )
        
    reply_html = render_to_string('articles/comment.html', {'comment': reply}, request=request)

    # Apply render_mentions filter to the rendered HTML
    #reply_html = Template("{% load comment_tags %}" + reply_html).render(Context({'comment': reply}))

    return JsonResponse({
        'success': True,
        'reply_html': reply_html,
        'comment_count': parent_comment.article.comment_count
    })




def create_follower_notifications(sender, article, comment, notification_type):
    current_time = timezone.now()
    notification_text = f"{sender.username} mentioned all followers in a {'comment' if not comment.parent else 'reply'}"
    
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO notifications_notification (
                recipient_id, sender_id, notification_type, article_id, comment_id, 
                text, is_read, created_at
            )
            SELECT 
                from_user_id, %s, %s, %s, %s, 
                %s, %s, %s
            FROM 
                users_user_following
            WHERE 
                to_user_id = %s
        """, [
            sender.id, 
            notification_type, 
            article.id, 
            comment.id, 
            notification_text,
            False,
            current_time,
            sender.id
        ])



def process_mentions(comment, user):
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, comment.content)
    followers_mentioned = False
    for index, username in enumerate(mentions):
        if username == 'followers':
            if not followers_mentioned:
                create_follower_notifications(user, comment.article, comment, 'mention')
                followers_mentioned = True
        else:
            mentioned_user = User.objects.filter(username=username).first()
            if mentioned_user:
                Mention.objects.create(user=mentioned_user, comment=comment, position=index)
                create_notification(
                    recipient=mentioned_user,
                    notification_type='mention',
                    sender=user,
                    article=comment.article,
                    comment=comment
                )


def get_tags(request):
    query = request.GET.get('query', '')
    tags = Tag.objects.filter(name__icontains=query).values_list('name', flat=True)
    return JsonResponse(list(tags), safe=False)



def user_suggestions(request):
    query = request.GET.get('query', '')
    user = request.user
    suggestions = list(User.objects.filter(
        Q(username__istartswith=query) | Q(first_name__istartswith=query) | Q(last_name__istartswith=query)
    ).exclude(id=user.id).values('id', 'username', 'first_name', 'last_name')[:10])
    
    if user.followers.exists() and '@followers'.startswith(query.lower()):
        suggestions.append({'id': 'followers', 'username': '@followers', 'first_name': 'All', 'last_name': 'Followers'})

    return JsonResponse([{
        'id': suggestion['id'],
        'username': suggestion['username'],
        'name': f"{suggestion['first_name']} {suggestion['last_name']}".strip()
    } for suggestion in suggestions], safe=False)



@csrf_exempt
@require_POST
def upload_image(request):
    if 'image' in request.FILES:
        image = request.FILES['image']
        ext = os.path.splitext(image.name)[1]
        filename = f"{uuid4().hex}{ext}"
        
        # Use Django's storage system for file handling
        path = default_storage.save(f'article_images/{filename}', ContentFile(image.read()))
        
        return JsonResponse({
            'success': 1,
            'file': {
                'url': default_storage.url(path),
            }
        })
    return JsonResponse({'success': 0})

