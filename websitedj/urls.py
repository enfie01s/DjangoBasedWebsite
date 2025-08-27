from django.conf.urls import include
from django.urls import re_path as url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from minecraft import views
from shows import views
import sitepages.views
from blog import views
from portfolio import views
from accounts import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^vegemites/', include('minecraft.urls')),
    url(r'^shows/', include('shows.urls')),
    url(r'^blog/', include('blog.urls')),
    url(r'^portfolio/', include('portfolio.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^', include('sitepages.urls')),
    url(r'^$',sitepages.views.home, name='home'),
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
