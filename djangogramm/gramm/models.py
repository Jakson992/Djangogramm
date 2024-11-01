from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from easy_thumbnails.fields import ThumbnailerImageField


class User(AbstractUser):
    email = models.EmailField(
        _('email address'),
        unique=True,
    )

    email_verify = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Post(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    tags = TaggableManager(blank=True)
    likes = models.ManyToManyField('User', blank=True, related_name='liked')
    creation_date = models.DateTimeField('User', auto_now=True)


class Image(models.Model):
    # image = models.ImageField(upload_to='images/%Y/%m/%d')
    image = ThumbnailerImageField(upload_to='images/%Y/%m/%d')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')