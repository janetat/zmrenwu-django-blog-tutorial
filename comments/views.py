from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post

from .forms import CommentForm


# Create your views here.
def post_comment(request, post_pk):
    # 先获取被评论的post, 因为后面需要把comment和post关联起来。
    post = get_object_or_404(Post, pk=post_pk)

    # 用户通过表单提交数据是通过POST请求
    if request.method == 'POST':
        # request.POST保存了用户提交的数据，然后用这些数据构造一个表单实例(因为form.is_valid可以自动帮我们检查数据是否符合格式要求)
        form = CommentForm(request.POST)

        # 检查表单的数据是否符合格式要求
        if form.is_valid():
            # 检查到数据合法, 利用表单的save方法将数据保存到数据库中
            comment = form.save(commit=False)
            # 将评论和被评论的文章关联起来
            comment.post = post
            comment.save()
            # redirect会调用模型实例的get_absolute_url, 然后重定向至得到的URL
            return redirect(post)
        else:
            # 数据不合法时，重新渲染详情页
            # Post(一)和Comment是ForeignKey(多)关联的，xxx_set.all()是反向引用全部评论(xxx_set实质是类似objects的模型管理器)。
            comment_list = post.comment_set.all()
            context = {
                'post': post,
                'form': form,
                'comment_list': comment_list
            }

            return render(request, 'blog/detail.html', context=context)

    # 不是POST请求，用户没有提交表单数据，重定向到文章详情页
    return redirect(post)
