from django import forms
from django.contrib import admin

from .forms import PostForm
from .models import Post, Category, Author, PostCategory

# Register your models here.


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    filter_horizontal = ('postCategory',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Author)
