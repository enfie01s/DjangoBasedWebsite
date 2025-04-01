from django.conf.urls import url
from . import views

app_name='sitepages'

urlpatterns = [
    #url(r'^create/', views.create, name='create'), 
    url(r'^$', views.home, name='home'),
    url(r'^homepage/$', views.homepage, name='homepage'),
    url(r'^mat/$', views.mat, name='mat'),
    url(r'^stella/$', views.stella, name='stella'),
]
