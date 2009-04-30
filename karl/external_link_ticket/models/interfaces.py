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


from zope.interface import Attribute
from zope.interface import Interface

class ILinkTickets(Interface):
    pass

class ILinkTicket(Interface):
    email = Attribute(u'The email address of the user the ticket was generated for')
    external_url = Attribute(u'The external url the ticket was issued for')
    remote_addr = Attribute(u'The ip address of the user requesting the ticket')
    created = Attribute(u'The date/time the ticket was created')
    used = Attribute(u'The date/time the ticket was used')
