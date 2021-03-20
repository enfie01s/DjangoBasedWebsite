from django.conf.urls import url, static
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name='portfolio'

urlpatterns = [
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<seotitle>[\d\w\-]+)/$', views.portfolio_post, name='portfolio_post'), 
    url(r'^manage(?:/(?P<pk>[\d\w\-]+))?', views.manage, name='manage'),
    url('', views.home, name='home'),
]
