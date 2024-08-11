from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import UserProfileForm, CustomLoginForm, CustomSignupForm
from .services import toggle_follow, toggle_block
from articles.models import Article
from django.contrib import messages
from django.contrib.auth import login
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from django.shortcuts import render, redirect


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
        context['articles'] = Article.objects.filter(author=self.object, status='published').order_by('-published_at')[:10]
        context['avatar_url'] = self.request.user.get_avatar_url()
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

class ActivityFeedView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'users/activity_feed.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.get_recent_articles_for_user(self.request.user)



@login_required
def toggle_premium(request):
    request.user.is_premium = not request.user.is_premium
    request.user.save()
    status = "activated" if request.user.is_premium else "deactivated"
    messages.success(request, f"Premium status {status}.")
    return redirect('user_profile', username=request.user.username)




def custom_login(request):
    if request.user.is_authenticated:
        return redirect('article_list')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            from allauth.account.auth_backends import AuthenticationBackend
            user = AuthenticationBackend().authenticate(
                request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user,backend='allauth.account.auth_backends.AuthenticationBackend')
                messages.success(request, 'Successfully logged in.')
                return redirect('article_list')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def custom_signup(request):
    if request.user.is_authenticated:
        return redirect('article_list')
    
    if request.method == 'POST':
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            complete_signup(request, user, app_settings.EMAIL_VERIFICATION, 'home')
            messages.success(request, 'Account created successfully. Please check your email for verification.')
            return redirect('article_list')
    else:
        form = CustomSignupForm()
    return render(request, 'accounts/signup.html', {'form': form})