from django import forms
from django.contrib.auth.forms import UserCreationForm

from watchBlogProject.watch_blog_app.models import User, Comment, Category, Post


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class LoginForm(forms.Form):
    email = forms.CharField()
    password = forms.CharField()


class ProfileEditForm(forms.Form):
    MAX_LENGTH_USERNAME = 30

    username = forms.CharField(
        max_length=MAX_LENGTH_USERNAME,
    )

    about_me = forms.CharField(
        widget=forms.Textarea(),
        required=False,
    )

    image = forms.ImageField(
        required=False,
    )

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def clean_username(self):
        username = self.cleaned_data['username']
        if username != self.original_username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('A user with that username already exists.')
        return username


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 'image', 'category', 'tags')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
