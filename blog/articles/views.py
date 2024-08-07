from django.shortcuts import render

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
from django.db import IntegrityError
from django.db.models import Count
import re
from django.db.models import Q


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
            response=super().form_valid(form)
            self.process_mentions(form.instance)
            # Create notification for the article author
            create_notification(
                recipient=article.author,
                notification_type='comment',
                sender=self.request.user,
                article=article,
                comment=self.object
            )
            return response
    def process_mentions(self, comment):
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, comment.content)
        for index, username in enumerate(mentions):
            if username == 'followers':
                for follower in self.request.user.followers.all():
                    Mention.objects.create(user=follower, comment=comment, position=index)
            else:
                user = User.objects.filter(username=username).first()
                if user:
                    Mention.objects.create(user=user, comment=comment, position=index)
                    create_notification(
                        recipient=user,
                        notification_type='mention',
                        sender=self.request.user,
                        article=comment.article,
                        comment=comment
                    )





    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk': self.kwargs['pk']})

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_form.html'
    success_url = reverse_lazy('article_list')

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)
    

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
        
        return redirect('article_detail', pk=parent_comment.article.pk)
    return redirect('article_detail', pk=parent_comment.article.pk)

def process_mentions(comment, user):
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, comment.content)
    for index, username in enumerate(mentions):
        if username == 'followers':
            for follower in user.followers.all():
                Mention.objects.create(user=follower, comment=comment, position=index)
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