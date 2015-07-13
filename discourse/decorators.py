"""
The decorators used by the SSO application
"""
import logging
from django.conf import settings
from django.http import HttpResponseBadRequest

Log = logging.getLogger('discourse.views.decorators')


def get_discourse_request_host(function):
	def decorator(*args, **kwargs):
		req = args[0]
		host = req.META.get('HTTP_HOST')
		referer = req.META.get('HTTP_REFERER')

		Log.info('host: %s' % host)
		Log.info('referer: %s' % referer)

		if referer and host not in referer:
			if referer not in settings.DISCOURSE_BASE_URLS:
				Log.error('Process originated from an unknown place. The refferer %s is not allowed.' % referer)
				return HttpResponseBadRequest(
				'Process originated from an unknown place. Please contact support if this problem persists.')

			req.session['referer'] = req.META.get('HTTP_REFERER')
			Log.info('User comes from %s' % req.session['referer'])
		else:
			Log.error('User originates from the current host %s, but it should from one of the approved '
					  'discourse instances.' % host)

		return function(*args, **kwargs)

	return decorator

