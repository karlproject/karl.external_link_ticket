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
from zope.testing.cleanup import cleanUp

from repoze.bfg import testing

class TestFindLinkTickets(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context):
        from karl.external_link_ticket.views.utils import find_link_tickets
        return find_link_tickets(context)

    def test_valid_created(self):
        context = testing.DummyModel()
        result = self._callFUT(context)
        self.assertEqual(result.__name__, 'link_tickets')

    def test_valid_existing(self):
        context = testing.DummyModel()
        link_tickets = testing.DummyModel(title='existing link tickets')
        context['link_tickets'] = link_tickets
        result = self._callFUT(context)
        self.assertEqual(result.__name__, 'link_tickets')
        self.assertEqual(result.title, 'existing link tickets')


class TestGenerateTicket(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, email, remote_addr, external_url):
        from karl.external_link_ticket.views.utils import generate_ticket
        return generate_ticket(context, email, remote_addr, external_url)

    def test_valid(self):
        context = testing.DummyModel()
        key = self._callFUT(context, 'test@example.com', '192.168.1.1', 'http://example.com')
        self.assertEqual(len(key), 32)


class TestWriteTicket(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()    

    def _callFUT(self, context, ticket, key):
        from karl.external_link_ticket.views.utils import write_ticket
        return write_ticket(context, ticket, key)

    def test_it(self):
        ticket = {
            'email': 'test@example.com',
            'remote_addr': '192.168.1.1', 
            'external_url': 'http://example.com',
        }
        key = '123456'
        context = testing.DummyModel()
        result = self._callFUT(context, ticket, key)
        ticket = context['link_tickets'][key]
        self.assertEqual(ticket.email, 'test@example.com')
        self.assertEqual(ticket.remote_addr, '192.168.1.1')
        self.assertEqual(ticket.external_url, 'http://example.com')
        self.failIf(ticket.created == None)
        self.failIf(getattr(ticket, 'used', 'no attribute') == 'no attribute')
        self.assertEqual(ticket.used, None)


class TestGetTicket(unittest.TestCase):
    def setUp(self):
        cleanUp()
    
    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, key):
        from karl.external_link_ticket.views.utils import get_ticket
        return get_ticket(context, key)

    def test_nonexisting(self):
        context = testing.DummyModel()
        context['link_tickets'] = testing.DummyModel()
        key = '123456'
        result = self._callFUT(context, key)
        self.assertEqual(result, None)
    
    def test_valid(self):
        from datetime import datetime
        created = datetime.now()
        context = DummyTicketContext(**{'created': created})

        key = '123456'
        result = self._callFUT(context, key)
        self.assertEqual(result['email'], 'test@example.com')
        self.assertEqual(result['created'], created)
        self.assertEqual(result['remote_addr'], '192.168.1.1')
        self.assertEqual(result['external_url'], 'http://example.com')
        self.assertEqual(result['used'], None)


class TestGetTicketAge(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _callFUT(self, ticket):
        from karl.external_link_ticket.views.utils import get_ticket_age
        return get_ticket_age(ticket)

    def test_valid(self):
        from datetime import datetime
        import time
        ticket = {'created': datetime.now()}
        result = self._callFUT(ticket)
        self.assertEqual(result, 0)


class TestValidateTicket(unittest.TestCase):
    def setUp(self):
        cleanUp()
    
    def tearDown(self):
        cleanUp()

    def _callFUT(self, ticket, remote_addr, external_url):
        from karl.external_link_ticket.views.utils import validate_ticket
        return validate_ticket(ticket, remote_addr, external_url)

    def test_invalid_expired(self):
        from datetime import datetime
        created = datetime(1999,1,1)
        remote_addr = '192.168.1.1'
        external_url = 'http://example.com'
        ticket = {
            'email': 'test@example.com',
            'remote_addr': remote_addr,
            'external_url': external_url,
            'created': created,
            'used': None,
        }
        result = self._callFUT(ticket, remote_addr, external_url)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['message'], 'The ticket is expired')

    def test_invalid_used(self):
        from datetime import datetime
        used = datetime(1999,1,1)
        remote_addr = '192.168.1.1'
        external_url = 'http://example.com'
        ticket = {
            'email': 'test@example.com',
            'remote_addr': remote_addr,
            'external_url': external_url,
            'created': datetime.now(),
            'used': used,
        }
        result = self._callFUT(ticket, remote_addr, external_url)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['message'], 'The ticket was already used')

    def test_invalid_remote_addr(self):
        from datetime import datetime
        created = datetime.now()
        external_url = 'http://example.com'
        ticket = {
            'email': 'test@example.com',
            'remote_addr': '192.168.1.1',
            'external_url': external_url,
            'created': created,
            'used': None,
        }
        result = self._callFUT(ticket, '192.168.1.2', external_url)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['message'], 'The ticket was generated for a different IP address')

    def test_invalid_external_url(self):
        from datetime import datetime
        created = datetime.now()
        remote_addr = '192.168.1.1'
        ticket = {
            'email': 'test@example.com',
            'remote_addr': remote_addr,
            'external_url': 'http://example.com',
            'created': created,
            'used': None,
        }
        result = self._callFUT(ticket, remote_addr, 'http://example.com/invalid')
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['message'], 'The ticket was generated for a different external_url')
        

    def test_valid(self):
        from datetime import datetime
        created = datetime.now()
        email = 'test@example.com'
        remote_addr = '192.168.1.1'
        external_url = 'http://example.com'
        ticket = {
            'email': 'test@example.com',
            'remote_addr': remote_addr,
            'external_url': external_url,
            'created': created,
            'used': None,
        }
        result = self._callFUT(ticket, remote_addr, external_url)
        self.assertEqual(result['status'], 'SUCCESS')
        self.assertEqual(result['email'], email)


class TestExpireTicket(unittest.TestCase):
    def setUp(self):
        cleanUp()
    
    def tearDown(self):
        cleanUp()

    def _callFUT(self, context, key):
        from karl.external_link_ticket.views.utils import expire_ticket
        return expire_ticket(context, key)

    def test_nonexisting(self):
        context = testing.DummyModel()
        result = self._callFUT(context, '123456')
        self.assertEqual(result, False)

    def test_valid(self):
        context = DummyTicketContext()
        result = self._callFUT(context, '123456')
        self.assertEqual(result, True)
        self.assertEqual(context['link_tickets'].get('123456',None), None)

class DummyTicketContext(testing.DummyModel):
    def __init__(self, **kw):
        testing.DummyModel.__init__(self)
        from datetime import datetime
        self['link_tickets'] = testing.DummyModel()
        ticket = testing.DummyModel()
        ticket.email = kw.get('email', 'test@example.com')
        ticket.remote_addr = kw.get('remote_addr', '192.168.1.1')
        ticket.external_url = kw.get('external_url', 'http://example.com')
        ticket.created = kw.get('created', datetime.now())
        ticket.used = kw.get('used', None)
        self['link_tickets']['123456'] = ticket