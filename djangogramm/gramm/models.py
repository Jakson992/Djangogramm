from cloudinary.models import CloudinaryField
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
    avatar = CloudinaryField('avatars', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Post(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='posts')
    tags = TaggableManager(blank=True)
    likes = models.ManyToManyField('User', blank=True, related_name='liked')
    creation_date = models.DateTimeField('User', auto_now=True)

    def __str__(self):
        return f"{self.author.email} - {self.creation_date}"

class Image(models.Model):
    image = CloudinaryField('images')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        return f"Image for post {self.post.id}"


class AuthorFollower(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='author')
    follower = models.ForeignKey('User', on_delete=models.CASCADE, related_name='follower')

    class Meta:
        unique_together = ('author', 'follower')
