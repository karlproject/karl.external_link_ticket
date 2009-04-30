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
from karl import testing as karltesting
from repoze.lemonade.testing import registerContentFactory
from karl.models.interfaces import IProfile

class SyncStaffRunnerTests(unittest.TestCase):

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def _getTargetClass(self):
        from karl.peopledir.scripts.sync_osi_staff import SyncStaff
        return SyncStaff

    def _makeOne(self, args=(), test_file='test1.xml'):
        # Load some default data from the sampledata dir
        from os.path import join
        from repoze.bfg.path import package_path
        from karl.peopledir import scripts
        scripts_path = package_path(scripts)

        full_sync_file = join(scripts_path, 'sampledata', test_file)
        argv = ['testing'] + list(args) + [full_sync_file]
        sync_staff = self._getTargetClass()(argv, testing=True)
        return sync_staff

    def test___init___defaults(self):
        sync_staff = self._makeOne(test_file='test1.xml')
        self.assertEqual(sync_staff.zodb_uri, 'zeo://localhost:8884')
        self.assertEqual(sync_staff.sync_file[-9:], 'test1.xml')

    def test_wellformed(self):
        sync_staff = self._makeOne(test_file='test1.xml')
        sync_staff.loadXML()
        self.assertEqual(sync_staff.xml_root.tag, 'users')

    def test_not_wellformed(self):
         from lxml.etree import XMLSyntaxError
         sync_staff = self._makeOne(test_file='test2.xml')
         self.assertRaises(XMLSyntaxError, sync_staff.loadXML)

    def test_wellformed_invalid(self):
        from lxml.etree import DocumentInvalid
        sync_staff = self._makeOne(test_file='test3.xml')
        sync_staff.validate = True
        self.assertRaises(DocumentInvalid, sync_staff.loadXML)

# Skip this because we aren't refactoring deeply inside sync.py to
# eliminate passing around XML.

#     def test_normalize_users(self):
#         sync_staff = self._makeOne(test_file='test4.xml')
#         sync_staff.loadXML()
#         users = sync_staff.normalize_users()
#         self.assertEqual(users, _sample_data_test4)

    def test_add_new_user(self):
        # registration
        registerContentFactory(karltesting.DummyProfile, IProfile)

        sync_staff = self._makeOne(test_file='test4.xml')
        sync_staff.loadXML()

        # Fake out the wiring up of users etc.
        sync_staff.site = testing.DummyModel()
        sync_staff.profiles = testing.DummyModel()
        sync_staff.users = karltesting.DummyUsers()

        user1 = sync_staff.xml_root.find('user')
        username = user1.findtext('username')
        profile = sync_staff.add_new_user(user1)

        # Check users, groups, and profiles to see if they are there
        by_login = sync_staff.users._by_login
        self.assertEqual(by_login.keys(), [username])
        g = ['group.KarlAffiliate', 'group.BudapestAdmins',
            'group.BaltimoreAdmins', 'group.BrusselsHRAdmins',
            'group.BrusselsAdmins', 'group.BrusselsOMAdmins']
        user = by_login['CpeobsL']
        self.assertEqual(user['groups'], g)

        self.assertEqual(sync_staff.profiles.keys(), ['CpeobsL'])
        profile = sync_staff.profiles['CpeobsL']
        self.assertEqual(profile.firstname, 'Lsjtaujob')
        self.assertEqual(profile.lastname, 'Twfe')
        self.assertEqual(profile.email, 'twfel@dfv.iv')
        self.assertEqual(profile.location, 'Budapest')
        self.assertEqual(profile.country, 'Hungary')
        self.assertEqual(profile.languages,
                         'Hungarian English German French')

_sample_data_test4 = [
            {'username': 'CpeobsL',
             'firstname': 'Somefirst',
             'extension': None, 'lastname':
             'TheLastname',
             'phone': None,
             'organization': 'Major University',
             'position': 'Head of Mega Office',
             'email': 'xx@yy.hu',
             },
            {'username': 'another',
             'firstname': 'Linux',
             'extension': None,
             'lastname': 'Pauling',
             'phone': None,
             'organization': 'Medical World',
             'position': 'Research Director',
             'email': 'linux@pauling.hu',
             },
            ]
