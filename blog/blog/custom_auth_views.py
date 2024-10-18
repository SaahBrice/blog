from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def custom_logout(request):
    logout(request)
    return redirect('welcome')  
