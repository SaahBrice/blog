from django.urls import path
from .views import update_onesignal_id, toggle_premium, ActivityFeedView, UserListView, UserProfileView, UserProfileUpdateView, FollowingListView, FollowersListView, toggle_follow_view, toggle_block_view, custom_login, custom_signup

urlpatterns = [
    path('', UserListView.as_view(), name='user_list'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='user_profile_edit'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),
    path('following/', FollowingListView.as_view(), name='following_list'),
    path('followers/', FollowersListView.as_view(), name='followers_list'),
    path('follow/<str:username>/', toggle_follow_view, name='toggle_follow'),
    path('block/<str:username>/', toggle_block_view, name='toggle_block'),
    path('feed/', ActivityFeedView.as_view(), name='activity_feed'),
    path('toggle-premium/', toggle_premium, name='toggle_premium'),
    path('login/', custom_login, name='account_login'),
    path('signup/', custom_signup, name='account_signup'),
    path('update-onesignal-id/', update_onesignal_id, name='update_onesignal_id'),
]