from django.conf.urls import patterns, url
from discourse import views

urlpatterns = patterns(
	'',
	url(r'^sso/$', views.sso, name='discourse_sso'),
)
