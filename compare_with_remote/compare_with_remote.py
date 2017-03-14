# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import argparse
import io
import logging
import os
import re
import subprocess
import sys
import tarfile
import tempfile

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        description='compare two directories. Directories can get fetched via ssh first, then "meld" get called to copmare the directories. See https://github.com/guettli/compare-with-remote')
    parser.add_argument('--only-files-containing-pattern')
    parser.add_argument('directory_url_one', help='[[user@]remote-host:]dir', )
    parser.add_argument('directory_url_two', help='[[user@]remote-host:]dir', )
    args = parser.parse_args()
    tmp_dir_one = create_tmp_dir_and_fill_it_with_files(
        only_files_containing_pattern=args.only_files_containing_pattern,
        directory_url_as_string=args.directory_url_one)
    tmp_dir_two = create_tmp_dir_and_fill_it_with_files(
        only_files_containing_pattern=args.only_files_containing_pattern,
        directory_url_as_string=args.directory_url_two)
    diff_command = ['meld', tmp_dir_one, tmp_dir_two]
    logger.info('Calling %s' % diff_command)
    subprocess.call(diff_command)


class DirectoryURL(object):
    url = None

    def __init__(self, url):
        self.url = url

    @property
    def user_at_host_or_none(self):
        return self.parse_url(self.url)['user_at_host']

    @property
    def directory(self):
        return self.parse_url(self.url)['directory']

    _parse_url_regex = r'^((?P<user_at_host>([^@:\s]+@)?[^\s:@]+):)?(?P<directory>.*)$'

    @classmethod
    def parse_url(cls, url):
        match = re.match(cls._parse_url_regex, url)
        directory = match.groupdict()['directory']
        user_at_host = match.groupdict()['user_at_host']
        if user_at_host is None and '@' in directory:
            user_at_host = directory
            directory = ''
        return dict(user_at_host=user_at_host, directory=directory)


def create_tmp_dir_and_fill_it_with_files(directory_url_as_string, only_files_containing_pattern=None):
    filter_files_pipe = ''
    if only_files_containing_pattern:
        filter_files_pipe = '''xargs grep -liE '{}' | '''.format(only_files_containing_pattern)
    cmd = []
    directory_url = DirectoryURL(directory_url_as_string)
    shell = True
    if directory_url.user_at_host_or_none:
        cmd = ['ssh', directory_url.user_at_host_or_none]
        shell = False
    cmd.append('''find "{}" | {} tar --files-from=- -czf- '''.format(
        directory_url.directory, filter_files_pipe))
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    (stdoutdata, stderrdata) = pipe.communicate()
    temp_dir = tempfile.mkdtemp(prefix='compare_%s_' % string_to_save_file_name(directory_url_as_string))
    try:
        extract_tar_skip_hard_links(stdoutdata, temp_dir)
    except tarfile.ReadError as exc:
        logger.warn(exc)
        logger.warn('Size of stdout: %s stderr: %s' % (len(stdoutdata), stderrdata))
        sys.exit()
    dir_count = 0
    file_count = 0
    for root, dirs, files in os.walk(temp_dir):
        dir_count += len(dirs)
        file_count += len(files)
    logger.info('files were stored in {} {} files {} directories'.format(
        temp_dir, file_count, dir_count))
    return temp_dir


def extract_tar_skip_hard_links(stdoutdata, base_dir):
    # useless reinvention of extractall(). Needed to work around http://bugs.python.org/issue29612
    with tarfile.open(fileobj=io.BytesIO(stdoutdata)) as tar_obj:
        for member in tar_obj.getmembers():
            if member.islnk():
                continue
            tar_obj.extract(member, base_dir)


def string_to_save_file_name(my_string):
    return re.sub(r'[^a-zA-Z0-9_@:]', '_', my_string)
