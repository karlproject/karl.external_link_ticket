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
import random
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

from repoze.bfg.security import authenticated_userid
from karl.utils import find_profiles
from karl.utils import find_site
from karl.external_link_ticket.models.ticket import LinkTickets
from karl.external_link_ticket.models.ticket import LinkTicket

success_xml_template = """<?xml version="1.0"?>
<AuthenticateTicketResponse>
    <Status>%(status)s</Status>
    <Email>%(email)s</Email>
</AuthenticateTicketResponse>
"""

fail_xml_template = """<?xml version="1.0"?>
<AuthenticateTicketResponse>
    <Status>%(status)s</Status>
    <Message>%(message)s</Message>
</AuthenticateTicketResponse>
"""

# the number of seconds a ticket should stay active
ticket_ttl = 60

def find_link_tickets(context):
    site = find_site(context)
    link_tickets = site.get('link_tickets', None)
    if not link_tickets:
        link_tickets = LinkTickets()
        site['link_tickets'] = link_tickets
    return link_tickets


def generate_ticket(context, email, remote_addr, external_url):
    # generate a random 32 character string
    key = md5(str(random.random())).hexdigest()

    ticket = dict(
        email = email,
        remote_addr = remote_addr,
        external_url = external_url,
    )
    write_ticket(context, ticket, key)
    return key

    
def write_ticket(context, ticket, key):
    link_tickets = find_link_tickets(context)
    link_ticket = LinkTicket(**ticket)
    link_tickets[key] = link_ticket
    return link_ticket


#def __call__(self):
#    external_url = self.request.get('external_url')
#    if not external_url:
#        return 'ERROR: No external_url was passed'
#    get_var_prefix = '?'
#    if external_url.find('?') != -1:
#        get_var_prefix = '&'
#    key = self.generate_ticket(external_url)
#    # redirect user to external_url passing key
#    return self.request.RESPONSE.redirect('%s%skarl_authentication_ticket=%s' % (external_url, get_var_prefix, key))

def get_ticket(context, key):
    link_tickets = find_link_tickets(context)
    link_ticket = link_tickets.get(key, None)
    if not link_ticket:
        return None

    ticket = dict(
        email = link_ticket.email,
        remote_addr = link_ticket.remote_addr,
        external_url = link_ticket.external_url,
        created = link_ticket.created,
        used = link_ticket.used,
    )
    return ticket

def get_ticket_age(ticket):
    age = datetime.now() - ticket['created']
    return age.seconds
    
def validate_ticket(ticket, remote_addr, external_url):
    # Verify that the ticket exists
    if not ticket:
        return {'status': 'FAIL', 'message': 'No ticket found with key %s' % key}

    # verify the ticket has not been used
    if ticket['used']:
        return {'status': 'FAIL', 'message': 'The ticket was already used'}

    # verify that the ticket is not more than a minute old
    if get_ticket_age(ticket) > ticket_ttl:
        return {'status': 'FAIL', 'message': 'The ticket is expired'}

    # verify that the ticket was for the correct external_url
    if ticket['external_url'] != external_url:
        return {'status': 'FAIL', 'message': 'The ticket was generated for a different external_url'}

    # verify that the remote_addr is correct
    remote_addr = remote_addr
    if remote_addr != ticket['remote_addr']:
        return {'status': 'FAIL', 'message': 'The ticket was generated for a different IP address'}

    return {'status': 'SUCCESS', 'email': ticket['email']}


def expire_ticket(context, key):
    link_tickets = find_link_tickets(context)
    if key in link_tickets.keys():
        del(link_tickets[key])
        return True
    return False


#    def __call__(self):
#        response_values = self.validate_ticket()
#
#        # render response values into xml
#        if response_values['status'] == 'SUCCESS':
#            xml = success_xml_template % response_values
#        else:
#            xml = fail_xml_template % response_values
#
#        return xml
