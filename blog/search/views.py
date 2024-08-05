from django.shortcuts import render

from django.views.generic import FormView
from django.db.models import Q
from articles.models import Article
from .forms import SearchForm

class SearchView(FormView):
    template_name = 'search/search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        query = form.cleaned_data.get('query')
        tags = form.cleaned_data.get('tags')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        author = form.cleaned_data.get('author')

        articles = Article.objects.filter(status='published')

        if query:
            articles = articles.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            )

        if tags:
            articles = articles.filter(tags__in=tags).distinct()

        if date_from:
            articles = articles.filter(published_at__gte=date_from)

        if date_to:
            articles = articles.filter(published_at__lte=date_to)

        if author:
            articles = articles.filter(author=author)

        context = self.get_context_data(form=form, articles=articles)
        return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))