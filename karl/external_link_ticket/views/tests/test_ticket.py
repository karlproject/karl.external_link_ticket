# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


import unittest

from repoze.bfg import testing
from karl.external_link_ticket.testing import DummyTicketContext

class WrapExternalLinkViewTests(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from karl.external_link_ticket.views.ticket \
            import wrap_external_link_view
        return wrap_external_link_view(context, request)

    def test_invalid_no_external_url(self):
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest()
        try:
            response = self._callFUT(context, request)
        except ValueError, exception:
            self.assertEqual(str(exception), 'No external_url provided')
        else:
            self.fail('Expected a ValueError')

    def test_invalid_blank_external_url(self):
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest(params={'external_url': ''})
        try:
            response = self._callFUT(context, request)
        except ValueError, exception:
            self.assertEqual(str(exception), 'No external_url provided')
        else:
            self.fail('Expected a ValueError')

    def test_invalid_unauthenticated(self):
        from repoze.bfg.exceptions import Forbidden
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest(
                            params={'external_url': 'http://example.com'})
        try:
            response = self._callFUT(context, request)
        except Forbidden, exception:
            self.assertEqual(str(exception), 'You are not logged in')
        else:
            self.fail('Expected Unauthorized exception')

    def test_invalid_noprofile(self):
        from repoze.bfg.exceptions import Forbidden
        testing.registerDummySecurityPolicy(userid='testuser')
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        request = testing.DummyRequest(
                            params={'external_url': 'http://example.com'})
        try:
            response = self._callFUT(context, request)
        except Forbidden, exception:
            self.assertEqual(str(exception),
                             'No profile found for user testuser')
        else:
            self.fail('Expected Unauthorized exception')

    def test_valid_no_get_args(self):
        testing.registerDummySecurityPolicy(userid='testuser')
        context = testing.DummyModel()
        context['profiles'] = testing.DummyModel()
        profile = testing.DummyModel()
        profile.email = 'test@example.com'
        context['profiles']['testuser'] = profile
        request = testing.DummyRequest(
                        params={'external_url': 'http://example.com'})
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
        request = testing.DummyRequest(
                        params={'external_url':
                                    'http://example.com?arg1=val1&arg2=val2'})
        response = self._callFUT(context, request)
        location_parts = response.location.split('&')
        self.assertEqual(location_parts[0], 'http://example.com?arg1=val1')
        self.assertEqual(location_parts[1], 'arg2=val2')
        self.assertEqual(location_parts[2][:27], 'karl_authentication_ticket=')
        self.assertEqual(len(location_parts[2][27:]), 32)

class AuthenticateTicketViewTests(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from karl.external_link_ticket.views.ticket \
            import authenticate_ticket_view
        return authenticate_ticket_view(context, request)

    def test_invalid_no_key(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'external_url': 'http://example.com',
            'remote_addr': '192.168.1.1',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL', 'message': 'No key provided'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_invalid_blank_key(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        key = None
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'ticket': key,
            'external_url': 'http://example.com',
            'remote_addr': '192.168.1.1',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL', 'message': 'No key provided'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_invalid_no_external_url(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'ticket': '123456',
            'remote_addr': '192.168.1.1',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL',
                           'message': 'No external_url provided'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_invalid_blank_external_url(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'ticket': '123456',
            'external_url': None,
            'remote_addr': '192.168.1.1',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL',
                           'message': 'No external_url provided'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_invalid_no_remote_addr(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'ticket': '123456',
            'external_url': 'http://example.com',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL',
                           'message': 'No remote_addr provided'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_invalid_blank_remote_addr(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        key = '123456'
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'ticket': key,
            'external_url': 'http://example.com',
            'remote_addr': None,
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL',
                           'message': 'No remote_addr provided'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_invalid_key(self):
        from karl.external_link_ticket.views.ticket import fail_xml_template
        context = testing.DummyModel()
        request = testing.DummyRequest(params={
            'ticket': '123456',
            'external_url': 'http://example.com',
            'remote_addr': '192.168.1.1',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'FAIL',
                           'message': 'No ticket matching key was found'}
        self.assertEqual(response.body, fail_xml_template % expected_status)

    def test_valid(self):
        from karl.external_link_ticket.views.ticket import success_xml_template
        context = DummyTicketContext()
        request = testing.DummyRequest(params={
            'ticket': '123456',
            'external_url': 'http://example.com',
            'remote_addr': '192.168.1.1',
        })
        response = self._callFUT(context, request)
        expected_status = {'status': 'SUCCESS', 'email': 'test@example.com'}
        self.assertEqual(response.body, success_xml_template % expected_status)
