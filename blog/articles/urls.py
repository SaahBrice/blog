from django.urls import path,include
from .views import (WelcomeView,upload_image,user_suggestions,get_tags, add_reply, toggle_comment_reaction, 
                    remove_bookmark, BookmarkedArticlesView, toggle_reaction, toggle_bookmark, toggle_follow_author, 
                    ArticlesByTagView, CommentCreateView, ArticleListView, ArticleDetailView, ArticleCreateView, ArticleUpdateView
                    )

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('articles/', ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', ArticleUpdateView.as_view(), name='article_update'),
    path('articles/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_create'),
    path('articles/tag/<slug:tag_slug>/', ArticlesByTagView.as_view(), name='article_by_tag'),
    path('articles/<int:pk>/bookmark/', toggle_bookmark, name='toggle_bookmark'),
    path('articles/follow-author/<int:author_id>/', toggle_follow_author, name='toggle_follow_author'),
    path('articles/<int:pk>/react/', toggle_reaction, name='toggle_reaction'),
    path('articles/bookmarked/', BookmarkedArticlesView.as_view(), name='bookmarked_articles'),
    path('articles/remove-bookmark/<int:pk>/', remove_bookmark, name='remove_bookmark'),
    path('articles/comment/<int:comment_id>/react/', toggle_comment_reaction, name='toggle_comment_reaction'),
    path('articles/comment/<int:comment_id>/reply/', add_reply, name='add_reply'),
    path('articles/get-tags/', get_tags, name='get_tags'),
    path('articles/user-suggestions/', user_suggestions, name='user_suggestions'),
    path('articles/upload-image/', upload_image, name='upload_image'),
]