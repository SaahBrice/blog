from django.urls import path
from .views import UserProfileView, UserProfileUpdateView

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='user_profile_edit'),
]