from django.conf.urls import include
from django.urls import re_path as url
from django.conf import settings
from django.contrib import admin
from django.views.static import serve
from minecraft import views
#from shows import views
import sitepages.views
from blog import views
from portfolio import views
from accounts import views

urlpatterns = [
    # Uploaded files. Static files are served by WhiteNoise.
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^admin/', admin.site.urls),
    url(r'^vegemites/', include('minecraft.urls')),
#    url(r'^shows/', include('shows.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^portfolio/', include('portfolio.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^', include('sitepages.urls')),
    url(r'^$',sitepages.views.home, name='home'),
]

