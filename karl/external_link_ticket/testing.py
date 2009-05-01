from repoze.bfg import testing

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
