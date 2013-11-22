import unittest

from pyramid import testing
from karl.external_link_ticket.testing import DummyTicketContext

class TestFindLinkTickets(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, firstname, lastname, email, remote_addr,
                 external_url):
        from karl.external_link_ticket.views.utils import generate_ticket
        return generate_ticket(context, firstname, lastname,
                               email, remote_addr, external_url)

    def test_valid(self):
        context = testing.DummyModel()
        key = self._callFUT(context, 'firstname', 'lastname',
                            'test@example.com', '192.168.1.1', 'http://example.com')
        self.assertEqual(len(key), 32)


class TestWriteTicket(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
        context = DummyTicketContext(**{'created': created,
                                        'first_name': 'First',
                                        'last_name': 'Last'})

        key = '123456'
        result = self._callFUT(context, key)
        self.assertEqual(result['email'], 'test@example.com')
        self.assertEqual(result['created'], created)
        self.assertEqual(result['remote_addr'], '192.168.1.1')
        self.assertEqual(result['external_url'], 'http://example.com')
        self.assertEqual(result['used'], None)


class TestGetTicketAge(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, ticket):
        from karl.external_link_ticket.views.utils import get_ticket_age
        return get_ticket_age(ticket)

    def test_valid(self):
        from datetime import datetime
        ticket = {'created': datetime.now()}
        result = self._callFUT(ticket)
        self.assertEqual(result, 0)


class TestValidateTicket(unittest.TestCase):
    def setUp(self):
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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

    # The remote_addr check is commented out in code since it caused issues with VPN'ed connections
    #def test_invalid_remote_addr(self):
    #    from datetime import datetime
    #    created = datetime.now()
    #    external_url = 'http://example.com'
    #    ticket = {
    #        'email': 'test@example.com',
    #        'remote_addr': '192.168.1.1',
    #        'external_url': external_url,
    #        'created': created,
    #        'used': None,
    #    }
    #    result = self._callFUT(ticket, '192.168.1.2', external_url)
    #    self.assertEqual(result['status'], 'FAIL')
    #    self.assertEqual(result['message'], 'The ticket was generated for a different IP address')

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
            'first_name': 'First',
            'last_name': 'Last',
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
        testing.setUp()

    def tearDown(self):
        testing.tearDown()

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
