from django import template
from django.db.models.aggregates import Count
from ..models import Post, Category, Tag

register = template.Library()


@register.simple_tag
def get_recent_posts(num=5):
    """最新文章模板标签"""
    return Post.objects.all()[:num]


@register.simple_tag
def archives():
    """归档模板标签"""
    return Post.objects.dates('created_time', 'month', order='DESC')


@register.simple_tag
def get_categories():
    """分类模板标签"""
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_tags():
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
