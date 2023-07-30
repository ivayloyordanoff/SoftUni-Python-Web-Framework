from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models


class User(AbstractUser):
    MAX_LENGTH_USERNAME = 30

    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
    )

    email = models.EmailField(
        'email address',
        unique=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    about_me = models.TextField(
        blank=True,
    )

    image = models.ImageField(
        upload_to='images',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.user.username


class Category(models.Model):
    MAX_LENGTH_NAME = 30

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    MAX_LENGTH_NAME = 30

    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.name


class Post(models.Model):
    MAX_LENGTH_TITLE = 200
    MAX_LENGTH_SLUG = 200

    title = models.CharField(
        max_length=MAX_LENGTH_TITLE,
        db_index=True,
        null=False,
        blank=False,
    )

    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        db_index=True,
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    content = models.TextField(
        null=False,
        blank=False,
    )

    image = models.ImageField(
        upload_to='images',
        null=True,
        blank=True,
    )

    category = models.ManyToManyField(
        Category,
        blank=True,
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    updated_on = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    content = models.TextField(
        null=False,
        blank=False,
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    updated_on = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ('-created_on',)

    def __str__(self):
        return f'Comment by {self.author.username}'


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
    )

    liker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None,
    )

    def __str__(self):
        return f'{self.liker.username} likes {self.post}'
