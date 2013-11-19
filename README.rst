karl.external_link_ticket
=========================

A way to wrap external links with a ticket that can be validated by the
external system, thus acting as a psuedo SSO.

Explanation
===========

In KARL, we have some links in the OSF home page that go to external resources in the Business Center. However, in KARL, we do some wrapping of those external links:

- In KARL, the URL looks like:

 https://karl.soros.org/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step1.cfm

- The user clicks on that and goes to /wrap_external_link in KARL

- We then generate a "ticket" and store it in the KARL database

- The ticket has these fields: email, external_url, remote_addr, created, and used

- The ticket value is stored with a key that is a random 32 bit value

- We then redirect the user to the actual URL, adding:

   ?karl_authentication_ticket=32bitkey

 ...at the end.

In the external system, they then want to validate that KARL issued the value in the 32bitkey. That system:

- Sends a request to such as:

   https://karl.soros.org/authenticate_ticket

 ..with 'ticket', 'external_url', and 'remote_addr' in the data.

- We then "validate" the ticket:

 * Does it exist?

 * Has it been used?

 * Is it over a minute old?

 * Is it for the external URL that it was issued for?

- If not valid, we respond with an XML message indicating the failure

- If it is valid, we respond with a success message
