# Copyright (C) 2014 Diane Trout
#
# This package is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License Version 2.1
# as published by the Free Software Foundation or any newer version.

# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License Version 2.1 for more details.

# You should have received a copy of the GNU Lesser General Public
# License Version 2.1 along with this package; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

from setuptools import setup

setup(
    name='rdfmagic',
    version='0.1',
    description='IPython magic functions to make it easier'
                'to query Redland librdf triple stores',
    author='Diane Trout',
    author_email='diane@ghic.org',
    packages=['rdfmagic'],
    install_requires=['IPython >= 0.12'],
    test_suite='rdfmagic.test.test_rdfmagic.suite'
)
