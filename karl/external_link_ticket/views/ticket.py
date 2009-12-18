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


from webob.exc import HTTPFound
from webob import Response
from repoze.bfg.exceptions import Forbidden
from repoze.bfg.security import authenticated_userid
from karl.utils import find_profiles
from karl.external_link_ticket.views.utils import generate_ticket
from karl.external_link_ticket.views.utils import get_ticket
from karl.external_link_ticket.views.utils import validate_ticket
from karl.external_link_ticket.views.utils import expire_ticket

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

def wrap_external_link_view(context, request):
    external_url = request.params.get('external_url', None)
    remote_addr = request.environ.get('REMOTE_ADDR', None)

    if not external_url:
        raise ValueError, 'No external_url provided'

    profiles = find_profiles(context)
    userid = authenticated_userid(request)
    if not userid:
        raise Forbidden('You are not logged in')
    profile = profiles.get(userid)
    if not profile:
        raise Forbidden('No profile found for user %s' % userid)
    
    key = generate_ticket(context, profile.email, remote_addr, external_url)

    if external_url.find('?') != -1:
        location = '%s&karl_authentication_ticket=%s' % (external_url, key)
    else:
        location = '%s?karl_authentication_ticket=%s' % (external_url, key)
    return HTTPFound(location = location)


def authenticate_ticket_view(context, request):
    key = request.params.get('ticket', None)
    external_url = request.params.get('external_url', None)
    remote_addr = request.params.get('remote_addr', None)

    error = None
    if not key:
        error = {'status': 'FAIL', 'message': 'No key provided'}
    if not external_url:
        error = {'status': 'FAIL', 'message': 'No external_url provided'}
    if not remote_addr:
        error = {'status': 'FAIL', 'message': 'No remote_addr provided'}
    if error:
        xml_response = fail_xml_template % error
        return Response(xml_response)

    ticket = get_ticket(context, key)
    if not ticket:
        error = {'status': 'FAIL', 'message': 'No ticket matching key was found'}
        xml_response = fail_xml_template % error
        return Response(xml_response)
    
    validation_result = validate_ticket(ticket, remote_addr, external_url)    
    if validation_result['status'] == 'SUCCESS':
        expire_ticket(context, key)
        xml_response = success_xml_template % validation_result
    else: 
        xml_response = fail_xml_template % validation_result
     
    return Response(xml_response)
