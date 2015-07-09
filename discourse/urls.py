from django.conf.urls import patterns, url
from django.views.generic import TemplateView
from discourse import views

urlpatterns = patterns(
	'',
	url(r'^login/$', views.login, name='discourse_login'),
	url(r'^error/$', TemplateView.as_view(template_name='error_login_discourse.html'), name="error-login"),
)
