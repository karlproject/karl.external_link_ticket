import unittest
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

class WrapExternalLinkViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, request):
        from karl.external_link_ticket.views.ticket import wrap_external_link_view
        return wrap_external_link_view(context, request)

    def test_invalid_external_url(self):
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest()
        try:
            response = self._callFUT(context, request)
        except ValueError, exception:
            self.assertEqual(exception.message, 'No external_url provided')
        else:
            self.fail('Expected a ValueError')

    def test_invalid_unauthenticated(self):
        from repoze.bfg.security import Unauthorized
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest(params={'external_url': 'http://example.com'})
        try:
            response = self._callFUT(context, request)
        except Unauthorized, exception:
            self.assertEqual(exception.message, 'You are not logged in')
        else:
            self.fail('Expected Unauthorized exception')

    def test_invalid_noprofile(self):
        from repoze.bfg.security import Unauthorized
        testing.registerDummySecurityPolicy(userid='testuser')
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest(params={'external_url': 'http://example.com'})
        try:
            response = self._callFUT(context, request)
        except Unauthorized, exception:
            self.assertEqual(exception.message, 'No profile found for user testuser')
        else:
            self.fail('Expected Unauthorized exception')

    def test_valid_no_get_args(self):
        testing.registerDummySecurityPolicy(userid='testuser')
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        profile = testing.DummyModel()
        profile.email = 'test@example.com'
        context['profiles']['testuser'] = profile
        request = testing.DummyRequest(params={'external_url': 'http://example.com'})
        response = self._callFUT(context, request)
        location_parts = response.location.split('?')
        self.assertEqual(location_parts[0], 'http://example.com')
        self.assertEqual(location_parts[1][:27], 'karl_authentication_ticket=')
        self.assertEqual(len(location_parts[1][27:]), 32)

    def test_valid_with_get_args(self):
        testing.registerDummySecurityPolicy(userid='testuser')
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        profile = testing.DummyModel()
        profile.email = 'test@example.com'
        context['profiles']['testuser'] = profile
        request = testing.DummyRequest(params={'external_url': 'http://example.com?arg1=val1&arg2=val2'})
        response = self._callFUT(context, request)
        location_parts = response.location.split('&')
        self.assertEqual(location_parts[0], 'http://example.com?arg1=val1')
        self.assertEqual(location_parts[1], 'arg2=val2')
        self.assertEqual(location_parts[2][:27], 'karl_authentication_ticket=')
        self.assertEqual(len(location_parts[2][27:]), 32)

        
        
