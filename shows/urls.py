from django.urls import re_path as url
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views

app_name='shows'

urlpatterns = [
    url(r'^ajax/dl/$', views.dl, name='dl'),
    url(r'^ajax/dlm/$', views.dlm, name='dlm'),
    url(r'^manage(?:/(?P<seotitle>[\d\w\-]+))?', views.manage, name='manage'),
    url(r'^onbreak', views.onbreak, name='onbreak'),
    url(r'^movies/manage(?:/(?P<seotitle>[\d\w\-]+))?', views.managemovie, name='managemovie'),
    url(r'^movies', views.movies, name='movies'),
    url(r'^(?P<seotitle>[\d\w\-]+)$', views.series, name='series'),
    url('',views.home, name='home'),
]
    
