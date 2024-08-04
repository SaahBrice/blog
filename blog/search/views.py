from django.shortcuts import render

from django.db.models import Q
from django.views.generic import ListView
from articles.models import Article

class SearchView(ListView):
    model = Article
    template_name = 'search/search_results.html'
    context_object_name = 'results'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Article.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).distinct()
        return Article.objects.none()