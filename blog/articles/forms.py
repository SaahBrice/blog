from django import forms
from .models import Article, Comment
from taggit.forms import TagWidget

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'language', 'status', 'tags']
        widgets = {
            'content': forms.HiddenInput(),
            'tags': TagWidget(),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }