"""
The decorators used by the SSO application
"""
from django.conf import settings
from django.http import HttpResponseBadRequest


def get_discourse_request_host(function):
	def decorator(*args, **kwargs):
		req = args[0]
		host = req.META.get('HTTP_HOST')
		referer = req.META.get('HTTP_REFERER')

		if host not in referer:
			if referer not in settings.DISCOURSE_BASE_URLS:
				return HttpResponseBadRequest(
				'Process originated from an unknown place. Please contact support if this problem persists.')

			req.session['referer'] = req.META.get('HTTP_REFERER')

		return function(*args, **kwargs)

	return decorator

