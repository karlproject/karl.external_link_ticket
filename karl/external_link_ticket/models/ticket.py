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


from datetime import datetime
from zope.interface import implements
from repoze.folder import Folder
from persistent import Persistent
from karl.external_link_ticket.models.interfaces import ILinkTickets
from karl.external_link_ticket.models.interfaces import ILinkTicket

class LinkTickets(Folder):
    implements(ILinkTickets)

class LinkTicket(Persistent):
    implements(ILinkTicket)

    def __init__(self, **kw):
        self.email = kw.get('email')
        self.external_url = kw.get('external_url')
        self.remote_addr = kw.get('remote_addr')
        self.created = datetime.now()
        self.used = None
