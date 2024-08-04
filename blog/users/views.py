from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserProfileForm
from .services import toggle_follow, toggle_block
from articles.models import Article


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user_profile'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_following'] = self.request.user.following.filter(id=self.object.id).exists()
            context['is_blocked'] = self.request.user.blocked_users.filter(id=self.object.id).exists()
        context['articles'] = Article.objects.filter(author=self.object, status='published').order_by('-published_at')[:5]
        return context

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('user_profile', kwargs={'username': self.object.username})
    

class FollowingListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/following_list.html'
    context_object_name = 'following'

    def get_queryset(self):
        return self.request.user.following.all()

class FollowersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'users/followers_list.html'
    context_object_name = 'followers'

    def get_queryset(self):
        return self.request.user.followers.all()

@login_required
def toggle_follow_view(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if toggle_follow(request.user, user_to_follow):
        messages.success(request, f"You are now following {username}")
    else:
        messages.success(request, f"You have unfollowed {username}")
    return redirect('user_profile', username=username)

@login_required
def toggle_block_view(request, username):
    user_to_block = get_object_or_404(User, username=username)
    if toggle_block(request.user, user_to_block):
        messages.success(request, f"You have blocked {username}")
    else:
        messages.success(request, f"You have unblocked {username}")
    return redirect('user_profile', username=username)