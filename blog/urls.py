from django.conf.urls import url, static
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name='blog'

urlpatterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<seotitle>[\d\w\-]+)/$', views.blog_post, name='blog_post'), 
    url(r'^manage(?:/(?P<pk>[\d\w\-]+))?', views.manage, name='manage'),
    url('', views.home, name='home'),
]
