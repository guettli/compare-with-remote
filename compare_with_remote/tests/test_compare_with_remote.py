# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import unittest

from compare_with_remote.compare_with_remote import CompareURL, string_to_save_file_name


class MyTestCase(unittest.TestCase):
    def test_directory_url_parsing__directory(self):
        self.assertEqual({'user_at_host': None, 'directory_or_cmd': 'foo', 'scheme': 'dir'}, CompareURL.parse_url('foo'))
        self.assertEqual({'directory_or_cmd': '', 'user_at_host': 'foo', 'scheme': 'dir'}, CompareURL.parse_url('foo:'))
        self.assertEqual({'directory_or_cmd': '', 'user_at_host': 'user@foo', 'scheme': 'dir'}, CompareURL.parse_url('user@foo:'))
        self.assertEqual({'directory_or_cmd': '', 'user_at_host': 'user@foo', 'scheme': 'dir'}, CompareURL.parse_url('user@foo'))
        self.assertEqual({'directory_or_cmd': 'mydir', 'user_at_host': 'user@foo', 'scheme': 'dir'},
                         CompareURL.parse_url('user@foo:mydir'))
        self.assertEqual({'directory_or_cmd': '/mydir', 'user_at_host': 'user@foo', 'scheme': 'dir'},
                         CompareURL.parse_url('user@foo:/mydir'))

    def test_directory_url_parsing__command(self):
        self.assertEqual({'user_at_host': 'user@host', 'directory_or_cmd': 'psql -c "select app, name from django_migrations order by id;"', 'scheme': 'cmd'},
                         CompareURL.parse_url('cmd:user@host:psql -c "select app, name from django_migrations order by id;"'))

    def test_directory(self):
        self.assertEqual('mydir', CompareURL('user@foo:mydir').directory)
        self.assertEqual('', CompareURL('user@foo').directory)

    def test_user_at_host_or_none(self):
        self.assertEqual('user@foo', CompareURL('user@foo:mydir').user_at_host_or_none)
        self.assertEqual(None, CompareURL('/etc').user_at_host_or_none)

    def test_string_to_save_file_name(self):
        self.assertEqual('x@:_______x', string_to_save_file_name('x@:ä  .. /x'))
