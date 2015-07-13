import base64
import hashlib
import hmac
import logging
import urllib

from urlparse import parse_qs
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
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

    if None in [payload, signature]:
        Log.error('Payload or signature not existing for user %s' % request.user.email)
        return HttpResponseRedirect(reverse('error-login'))

    # Validating playload
    try:
        payload = urllib.unquote(payload)
        decoded = base64.decodestring(payload)
        assert 'nonce' in decoded
        assert len(payload) > 0
    except AssertionError:
        Log.error('Invalid plyload for user %s' % request.user.email)
        return HttpResponseBadRequest(
            'Invalid plyload. Please contact support if this problem persists')

    # Create key-hash message
    key = str(settings.DISCOURSE_SSO_SECRET)
    h = hmac.new(key, payload, digestmod=hashlib.sha256)
    this_signature = h.hexdigest()

    if this_signature != signature:
        Log.error('Signature for user %s is not correct' % request.user.email)
        return HttpResponseBadRequest(
            'Invalid payload. Please contact support if this problem persists.')

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



