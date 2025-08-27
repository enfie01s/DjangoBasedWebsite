from django.urls import re_path as url
from . import views

app_name='sitepages'

urlpatterns = [
    #url(r'^create/', views.create, name='create'), 
    url(r'^$', views.home, name='home'),
    url(r'^homepage/$', views.homepage, name='homepage'),
    url(r'^(?P<firstName>[\d\w\-]+)/$', views.contact, name='contact'),
]
