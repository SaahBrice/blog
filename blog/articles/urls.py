from django.urls import path,include
from .views import user_suggestions,get_tags, add_reply, toggle_comment_reaction, remove_bookmark, BookmarkedArticlesView, toggle_reaction, toggle_bookmark, toggle_follow_author, ArticlesByTagView, CommentCreateView, ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView

urlpatterns = [
    path('', ArticleListView.as_view(), name='article_list'),
    path('<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('create/', ArticleCreateView.as_view(), name='article_create'),
    path('<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_update'),
    path('<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('tag/<slug:tag_slug>/', ArticlesByTagView.as_view(), name='article_by_tag'),
    path('<int:pk>/bookmark/', toggle_bookmark, name='toggle_bookmark'),
    path('follow-author/<int:author_id>/', toggle_follow_author, name='toggle_follow_author'),
    path('<int:pk>/react/', toggle_reaction, name='toggle_reaction'),
    path('bookmarked/', BookmarkedArticlesView.as_view(), name='bookmarked_articles'),
    path('remove-bookmark/<int:pk>/', remove_bookmark, name='remove_bookmark'),
    path('comment/<int:comment_id>/react/', toggle_comment_reaction, name='toggle_comment_reaction'),
    path('comment/<int:comment_id>/reply/', add_reply, name='add_reply'),
    path('get-tags/', get_tags, name='get_tags'),
    path('user-suggestions/', user_suggestions, name='user_suggestions'),
    
]