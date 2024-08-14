from django import forms
from .models import User as TUser
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm


User = get_user_model()

class CustomLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full px-3 py-2 border rounded-md'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email address.")
        return email

class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'w-full px-3 py-2 border rounded-md'})
        self.fields['password1'].widget.attrs.update({'class': 'w-full px-3 py-2 border rounded-md'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full px-3 py-2 border rounded-md'})

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account already exists with this email address.")
        return email



class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'imageUpload'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class':'w-full '}), required=False)
    location = forms.CharField(max_length=100, required=False)
    website = forms.URLField(required=False)
    class Meta:
        model = TUser
        fields = ['username', 'email', 'bio', 'profile_picture', 'location', 'website']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['profile_picture'].initial = self.instance.profile_picture