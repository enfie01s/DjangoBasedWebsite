from django.conf.urls import url
from . import views

app_name='minecraft'

urlpatterns = [
    url(r'^$',views.home, name='home'),
    url(r'^players/(?P<playername>[\w\d\-]+)/$', views.player, name='player'),
    url(r'^players/$', views.players, name = 'players'),
    url(r'^commands/$', views.commands, name = 'commands'),
    url(r'^info/$', views.info, name = 'info'),
    url(r'^gallery(?:/(?P<player>[\d\w\-]+))?$', views.gallery, name = 'gallery'),
    #url(r'^create/', views.create, name='create'), 
]