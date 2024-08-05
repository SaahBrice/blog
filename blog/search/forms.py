from django import forms
from taggit.models import Tag
from articles.models import Article
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search')
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    author = forms.ModelChoiceField(
        queryset=User.objects.filter(article__isnull=False).distinct(),
        required=False,
        empty_label="Any Author"
    )