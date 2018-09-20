import markdown
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from comments.forms import CommentForm
from .models import Post, Category


class IndexView(ListView):
    # get_queryset()对Post进行操作
    model = Post
    template_name = 'blog/index.html'
    # 获取Post列表数据，并保存到post_list中
    context_object_name = 'post_list'
    # 如果在FBV中分页，要用到Django的Paginator。在CBV中，用属性
    paginate_by = 3


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    # get_object, get_context_data都是辅助方法，都会在get中调用
    def get(self, request, *args, **kwargs):
        """get方法最终会返回一个HTTPResponse"""
        # 调用父类的get, 才有self.object
        response = super().get(request, *args, **kwargs)

        # 文章阅读量+1。这里的object就是get_object()返回的object, 就是文章post的一个实例
        self.object.increase_page_view()

        return response

    def get_object(self, queryset=None):
        """在这里对post的body的值解析为Markdown"""
        post = super().get_object(queryset=None)
        post.body = markdown.markdown(post.body,
                                      extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc'
                                      ])
        return post

    def get_context_data(self, **kwargs):
        """传递除context_object_name以外的变量到模板"""
        context = super().get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form': form,
            'comment_list': comment_list,
        })
        return context


class ArchivesView(IndexView):
    def get_queryset(self):
        # 在类视图中，从 URL 捕获的命名组参数值保存在实例的 kwargs 属性（是一个字典）里，非命名组参数值保存在实例的 args 属性（是一个列表）里。原理看ContextMixin。
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super().get_queryset().filter(created_time__year=year, created_time__month=month)


class CategoryView(IndexView):
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        # 因为父类IndexView绑定了model = Post, 所以get_queryset对Post操作
        return super().get_queryset().filter(category=cate)
