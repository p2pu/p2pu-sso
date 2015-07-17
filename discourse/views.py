import base64
import hashlib
import hmac
import logging
import urllib
from urlparse import parse_qs

from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from .decorators import get_discourse_request_host

Log = logging.getLogger('discourse.views')

@get_discourse_request_host
@login_required
def login(request):
	referer = request.session.get('referer')
	payload = request.GET.get('sso')
	signature = request.GET.get('sig')

	if not payload and not signature:
		Log.error('Payload or signature not existing for user %s' % request.user.email)
		return HttpResponseRedirect(reverse('error-login'))

	# Validating playload
	try:
		payload = urllib.unquote(payload)
		decoded = base64.b64decode(payload)
		assert 'nonce' in decoded
		assert len(payload) > 0
	except TypeError:
		Log.error('Invalid payload for user %s' % request.user.email)
		messages.error(request, 'Something went wrong, please try again.')
		return HttpResponseRedirect(reverse('error-login'))
	except AssertionError:
		Log.error('Invalid payload for user %s' % request.user.email)
		messages.error(request, 'Something went wrong, please try again.')
		return HttpResponseRedirect(reverse('error-login'))

	# Create key-hash message
	key = str(settings.DISCOURSE_SSO_SECRET)
	h = hmac.new(key, payload, digestmod=hashlib.sha256)
	this_signature = h.hexdigest()

	if this_signature != signature:
		Log.error('Signature for user %s is invalid' % request.user.email)
		messages.error(request, 'Something went wrong, we can\'t connect you to'
		                        '<a href="">here</a>')
		return HttpResponseRedirect(reverse('error-login'))

	# Build the return payload
	qs = parse_qs(decoded)
	params = {
		'nonce': qs['nonce'][0],
		'email': request.user.email,
		'external_id': request.user.id,
		'username': request.user.username,
	}

	return_payload = base64.encodestring(urllib.urlencode(params))
	h = hmac.new(key, return_payload, digestmod=hashlib.sha256)
	query_string = urllib.urlencode({'sso': return_payload, 'sig': h.hexdigest()})

	# Redirect back to origin

	if referer not in settings.DISCOURSE_BASE_URLS:
		Log.error('Invalid referer for user %s. Referer: %s' % (request.user.email, referer))
		return HttpResponseRedirect(reverse('error-login'))

	url = '%s/session/sso_login' % referer

	return HttpResponseRedirect('%s?%s' % (url, query_string))

def logout(request):

	redirect_url = request.GET.get('next')
	auth_logout(request)

	if redirect_url:
		return HttpResponseRedirect(redirect_url)

	return HttpResponseRedirect('http://community.p2pu.org')




