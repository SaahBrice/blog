from django.shortcuts import render

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Article, Comment, Reaction
from .forms import ArticleForm, CommentForm
from taggit.models import Tag
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from users.models import User
from users.services import toggle_follow
from notifications.services import create_notification
from django.db import transaction


class ArticleListView(ListView):
    model = Article
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    queryset = Article.objects.filter(status='published').order_by('-published_at')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['recommended_articles'] = Article.get_recommended_articles(self.request.user)
        return context

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_following'] = self.request.user.following.filter(id=self.object.author.id).exists()
            context['is_bookmarked'] = self.object.is_bookmarked_by(self.request.user)
            context['comment_form'] = CommentForm()
            context['user_reactions'] = Reaction.objects.filter(user=self.request.user,article=self.object).values_list('reaction_type', flat=True)
        return context

class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    http_method_names = ['post']

    def form_valid(self, form):
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        form.instance.article = article
        form.instance.author = self.request.user
        return super().form_valid(form)

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
    
    if reaction_type not in dict(Reaction.REACTION_TYPES):
        return JsonResponse({'error': 'Invalid reaction type'}, status=400)
    
    with transaction.atomic():
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            article=article,
            reaction_type=reaction_type,
            defaults={'count': 1}
        )
    
        if not created:
            if reaction.count < 100:
                reaction.count += 1
                reaction.save()
            else:
                return JsonResponse({'error': 'Maximum reaction count reached'}, status=400)
    
    create_notification(article.author, reaction_type, sender=request.user, article=article)
    
    return JsonResponse({
        'clap_count': article.clap_count,
        'sad_count': article.sad_count,
        'laugh_count': article.laugh_count,
    })