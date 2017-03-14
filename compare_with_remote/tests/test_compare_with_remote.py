# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import unittest

from compare_with_remote.compare_with_remote import DirectoryURL, string_to_save_file_name


class MyTestCase(unittest.TestCase):
    def test_directory_url_parsing(self):
        self.assertEqual({'user_at_host': None, 'directory': 'foo'}, DirectoryURL.parse_url('foo'))
        self.assertEqual({'directory': '', 'user_at_host': 'foo'}, DirectoryURL.parse_url('foo:'))
        self.assertEqual({'directory': '', 'user_at_host': 'user@foo'}, DirectoryURL.parse_url('user@foo:'))
        self.assertEqual({'directory': '', 'user_at_host': 'user@foo'}, DirectoryURL.parse_url('user@foo'))
        self.assertEqual({'directory': 'mydir', 'user_at_host': 'user@foo'},
                         DirectoryURL.parse_url('user@foo:mydir'))
        self.assertEqual({'directory': '/mydir', 'user_at_host': 'user@foo'},
                         DirectoryURL.parse_url('user@foo:/mydir'))

    def test_directory(self):
        self.assertEqual('mydir', DirectoryURL('user@foo:mydir').directory)
        self.assertEqual('', DirectoryURL('user@foo').directory)

    def test_user_at_host_or_none(self):
        self.assertEqual('user@foo', DirectoryURL('user@foo:mydir').user_at_host_or_none)


    def test_string_to_save_file_name(self):
        self.assertEqual('x@:_______x', string_to_save_file_name('x@:ä  .. /x'))
