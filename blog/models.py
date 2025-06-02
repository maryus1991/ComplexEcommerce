from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

from django.contrib.auth import get_user_model

from stores.models import Store

User = get_user_model()

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='blog_categories/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogs')
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='blogs')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='blogs')
    content = RichTextUploadingField()
    image = models.ImageField(upload_to='blogs/', null=True)

    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class BlogTag(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class BlogView(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='views')
    ip = models.GenericIPAddressField()
    count = models.IntegerField(default=1)

    def __str__(self):
        return self.ip


