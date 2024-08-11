from django import forms
from .models import Article, Comment
from taggit.forms import TagWidget

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'language', 'status', 'tags','thumbnail']
        widgets = {
            'content': forms.HiddenInput(),
            'tags': TagWidget(),
        }
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            if thumbnail.size > 5 * 1024 * 1024:
                raise forms.ValidationError("The maximum file size that can be uploaded is 5 MB")
        return thumbnail
    

    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }
