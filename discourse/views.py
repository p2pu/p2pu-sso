import base64
import hashlib
import hmac
import urllib

from urlparse import parse_qs

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.conf import settings


@login_required
def sso(request):
	payload = request.GET.get('sso')
	signature = request.GET.get('sig')

	if None in [payload, signature]:
		return HttpResponseBadRequest(
			'No SSO Playload or signature. Please contact support if this problem persists.')

	# Validating playload
	try:
		payload = urllib.unquote(payload)
		decoded = base64.decodestring(payload)
		assert 'nonce' in decoded
		assert len(payload) > 0
	except AssertionError:
		return HttpResponseBadRequest(
			'Invalid plyload. Please contact support if this problem persists')

	# Create key-hash message
	key = str(settings.DISCOURSE_SSO_SECRET)
	h = hmac.new(key, payload, digestmod=hashlib.sha256)
	this_signature = h.hexdigest()

	if this_signature != signature:
		return HttpResponseBadRequest(
			'Invalid payload. Please contact support if this problem persists.')

	# TODO: Create user
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

	url = '%s/session/sso_login' % settings.DISCOURSE_BASE_URL

	return HttpResponseRedirect('%s?%s' % (url, query_string))



