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

class TestLinkTickets(unittest.TestCase):
    def _getTargetClass(self):
        from karl.external_link_ticket.models.ticket import LinkTickets
        return LinkTickets

    def _makeOne(self, **kw):
        return self._getTargetClass()(**kw)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.external_link_ticket.models.interfaces import ILinkTickets
        verifyClass(ILinkTickets, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.external_link_ticket.models.interfaces import ILinkTickets
        verifyObject(ILinkTickets, self._makeOne())

class TestLinkTicket(unittest.TestCase):
    def _getTargetClass(self):
        from karl.external_link_ticket.models.ticket import LinkTicket
        return LinkTicket

    def _makeOne(self, **kw):
        return self._getTargetClass()(**kw)

    def test_verifyImplements(self):
        from zope.interface.verify import verifyClass
        from karl.external_link_ticket.models.interfaces import ILinkTicket
        verifyClass(ILinkTicket, self._getTargetClass())

    def test_verifyProvides(self):
        from zope.interface.verify import verifyObject
        from karl.external_link_ticket.models.interfaces import ILinkTicket
        verifyObject(ILinkTicket, self._makeOne(
            email = 'test@example.com',
            external_url = 'http://example.com',
            remote_addr = '192.168.1.1',
        ))
