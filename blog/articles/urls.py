from django.urls import path,include
from .views import ArticlesByTagView, CommentCreateView, ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView

urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('create/', ArticleCreateView.as_view(), name='article_create'),
    path('<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_update'),
    path('<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('tag/<slug:tag_slug>/', ArticlesByTagView.as_view(), name='article_by_tag'),
    
]