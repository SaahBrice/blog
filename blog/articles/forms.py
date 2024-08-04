from django import forms
from .models import Article, Comment

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'language', 'status', 'tags']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }