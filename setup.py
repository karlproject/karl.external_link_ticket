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

__version__ = '0.1'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = ''
    CHANGES = ''

requires = ['setuptools', 'karl', 'repoze.session', 'repoze.browserid']

setup(name='karl.external_link_ticket',
      version=__version__,
      description='Content types for KARL',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        ],
      keywords='web wsgi karl',
      author="Open Society Institute",
      author_email="osi-dev@lists.palladion.com",
      url="http://launchpad.net/~teamkarl",
      license="GPL",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['karl'],
      zip_safe=False,
      #tests_require = require,
      install_requires = requires,
      test_suite="nose.collector",
      #entry_points = """\
      #[console_scripts]
      #remove_old_tickets = karl.external_link_ticket.scripts.remove_old_tickets:main      
      #"""
      )

