"""
Tests for loging in and signing up
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

# TODO:
# Tests needed for tasks:#
# * signup new user coming from discourse

class LoginDiscourseTests(TestCase):
	payload = 'bm9uY2U9OTNjNzcyMWEyNzc2ZjJmZGZmZWMwODhiYTRjNGJmODUmcmV0dXJu%0AX3Nzb191cmw9aHR0cCUzQSUyRiUyRmRxZXJpa2EucDJwdS5vcmclMkZzZXNz%0AaW9uJTJGc3NvX2xvZ2lu%0A'
	sig = '71154aefbe94005852e7918aceba7d98a58d7a0978d519a7779857ed8f854f31'

	response_redirect_url = 'http://testserver/session/sso_login?sso=bm9uY2U9OTNjNzcyMWEyNzc2ZjJmZGZmZWMwODhiYTRjNGJmODUmdXNlcm5hbWU9Zmlyc3RfdXNl%0AciZleHRlcm5hbF9pZD0xJmVtYWlsPW15ZW1haWwlNDB0ZXN0LmNvbQ%3D%3D%0A&sig=652b9db615be6a1827dbd71d8912c54cf34d0eb4612bd4e64bb1cd23f69afe0d'

	password = 'mypassword'

	def setUp(self):
		self.user = User.objects.create_user('first_user', 'myemail@test.com', self.password)
		self.client = Client()

	def test_call_discourse_login_view_denies_anonymous(self):
		response = self.client.get(reverse('discourse_login'), follow=True)
		self.assertRedirects(response, '%s?next=%s' % (reverse('account_login'), reverse('discourse_login')))
		response = self.client.post(reverse('discourse_login'), follow=True)
		self.assertRedirects(response, '%s?next=%s' % (reverse('account_login'), reverse('discourse_login')))

	def test_login_from_discourse_with_existing_user_and_all_the_payload_ok(self):
		self.client.login(username=self.user.username, password=self.password)
		self.assertIn('_auth_user_id', self.client.session)

		extra_headers = {'HTTP_REFERER': 'http://testserver', 'HTTP_HOST': '127.0.0.1'}

		response = self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), self.payload,
		                                                 self.sig), follow=False, **extra_headers)

		self.assertEquals(response['Location'], self.response_redirect_url)

	def test_login_corrupted_payload(self):
		self.client.login(username=self.user.username, password=self.password)
		extra_headers = {'HTTP_REFERER': 'http://testserver', 'HTTP_HOST': 'sso.p2pu.org'}

		response = self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), None, self.sig))

		self.assertRedirects(response, reverse('error-login'))

		self.assertRaises(TypeError,
		                  self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), '', self.sig),
		                                  follow=False, **extra_headers))
		self.assertRaises(TypeError,
		                  self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), '12345',
		                                                        self.sig),
		                                  follow=False, **extra_headers))
		self.assertRaises(TypeError,
		                  self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), 'dd12345fd=',
		                                                        self.sig),
		                                  follow=False, **extra_headers))

	def test_corrupted_signature(self):
		self.client.login(username=self.user.username, password=self.password)
		extra_headers = {'HTTP_REFERER': 'http://testserver', 'HTTP_HOST': 'sso.p2pu.org'}

		response = self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), self.payload, None))

		self.assertRedirects(response, reverse('error-login'))

		self.assertRaises(TypeError,
		                  self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), self.payload,
		                                                        '12345'),
		                                  follow=False, **extra_headers))
		self.assertRaises(TypeError,
		                  self.client.get('%s?sso=%s&sig=%s' % (reverse('discourse_login'), self.payload,
		                                                        '12345'),
		                                  follow=False, **extra_headers))

	def test_unapproved_referrerer(self):
		pass

	def test_localhost_refererer(self):
		pass




