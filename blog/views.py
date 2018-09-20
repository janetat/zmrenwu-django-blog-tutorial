import markdown
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from comments.forms import CommentForm
from .models import Post, Category, Tag


class IndexView(ListView):
    # get_queryset()对Post进行操作。
    model = Post
    template_name = 'blog/index.html'
    # 获取Post列表数据，并保存到post_list中。
    context_object_name = 'post_list'
    # 如果在FBV中分页，要用到Django的Paginator。在CBV中，用属性
    paginate_by = 3

    def get_context_data(self, **kwargs):
        """完善分页功能(不再只有上一页，下一页)"""
        # 父类的context，是一个字典。
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        # page是一个对象
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自定义方法获取新增的context分页变量
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        # 将新增的变量更新到context。此时context已有了显示分页导航条的数据。
        context.update(pagination_data)
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页，就没有必要return任何分页导航条的数据。
            return {}

        # 当前页要显示的左边、右边连续的页码
        left = []
        right = []
        # 表示第一页和最后一页是否需要显示省略号
        left_has_more = False
        right_has_more = False
        # 表示是否要显示第一页和最后一页
        first = False
        last = False

        # 当前页码
        page_number = page.number
        # 分页后的总页数
        total_pages = paginator.num_pages
        # 分页后的range
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页, left默认为空。
            # 这里只获取当前页码后连续两个页码
            right = page_range[page_number:page_number + 2]

            if right[-1] < total_pages - 1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
            # 如果用户请求的是最后一页，right默认为空。
            # 这里只获取当前页码前连续两个页码
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0: page_number - 1]

            # 如果最左边的页码比第二页页码大
            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True

        else:
            # 用户请求的是中间的页码
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0: page_number - 1]
            right = page_range[page_number:page_number + 2]

            # 是否需要显示最后一页和最后一页前的省略号
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 左边
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

            # context要更新的分页导航条的数据
        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }

        return data


# 简短写法
# def pagination_data(self, paginator, page, is_paginated):
#     if not is_paginated:
#         return {}
#     left = []
#     right = []
#     left_has_more = False
#     right_has_more = False
#     first = False
#     last = False
#
#     page_number = page.number
#     total_pages = paginator.num_pages
#     page_range = paginator.page_range
#
#     left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0:
#                       (page_number - 1) if (page_number - 1) > 0 else 0]
#     right = page_range[page_number:page_number + 2]
#
#     if right:
#         if right[-1] < total_pages:
#             last = True
#         if right[-1] < total_pages - 1:
#             right_has_more = True
#     if left:
#         if left[0] > 1:
#             first = True
#         if left[0] > 2:
#             left_has_more = True
#
#     data = {'left': left,
#             'right': right,
#             'left_has_more': left_has_more,
#             'right_has_more': right_has_more,
#             'first': first,
#             'last': last, }
#
#     return data


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    # get_object, get_context_data都是辅助方法，都会在get中调用
    def get(self, request, *args, **kwargs):
        """get方法最终会返回一个HTTPResponse"""
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


class TagView(IndexView):
    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super().get_queryset().filter(tags=tag)
