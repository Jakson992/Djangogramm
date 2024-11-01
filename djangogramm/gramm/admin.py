from django.contrib import admin

from .models import User, Post, Image

admin.site.register(User),
admin.site.register(Post),
admin.site.register(Image)