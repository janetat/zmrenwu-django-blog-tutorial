from django.urls import re_path

from . import views

app_name = 'blog'

urlpatterns = [
    re_path(r'^$', views.IndexView.as_view(), name='index'),
    re_path(r'^post/(?P<pk>[0-9]+)/$', views.PostDetailView.as_view(), name='detail'),
    re_path(r'^archives/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$', views.ArchivesView.as_view(), name='archives'),
    re_path(r'^category/(?P<pk>[0-9]+)/$', views.CategoryView.as_view(), name='category')
]


