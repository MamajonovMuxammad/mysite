from django import forms
from .models import Comment
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.models import User 


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                                widget=forms.Textarea)
    

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']  # Добавьте другие поля профиля пользователя при необходимости
    


class CommentForm(forms.ModelForm):
    class Meta:
            model = Comment
            fields = ['name', 'email', 'body','image']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']