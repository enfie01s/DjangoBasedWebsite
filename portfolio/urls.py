from django.conf.urls import url
from . import views

app_name='portfolio'

urlpatterns = [
    url(r'^$',views.home, name='home'),
    #url(r'^create/', views.create, name='create'), 
]