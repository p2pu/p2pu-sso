# Global urls

from django.conf.urls import include, url
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles import views

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^accounts/', include('allauth.urls')),
	url(r'^discourse/', include('discourse.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
