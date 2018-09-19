import markdown
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import strip_tags

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    created_time = models.DateTimeField()
    modified_time = models.DateTimeField()
    abstract = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # page_view网页阅读量
    page_view = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_time']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ 实现自动摘要
            方法一：在被保存到数据库之前，从body自动摘取前50个字符，成为摘要abstract。
            方法二：在模板中使用过滤器{{ post.body|truncatechars:54 }}，不过如果有html标签，会比较难看。
        """
        if not self.abstract:
            # 实例化Markdown类，用于渲染body文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 将Markdown转换成HTML，然后去掉HTML文本的全部标签，从文本摘取前50个字符赋给abstract
            self.abstract = strip_tags(md.convert(self.body))[:50]

        super(Post, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def increase_page_view(self):
        self.page_view += 1
        self.save(update_fields=['page_view'])

