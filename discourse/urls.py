from django.conf.urls import patterns, url
from discourse import views

urlpatterns = patterns(
	'',
	url(r'^login/$', views.login, name='discourse_login'),
)
