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
        description='compare two directories or command outputs. Data can get fetched via ssh first, then "meld" get called to copmare the data. See https://github.com/guettli/compare-with-remote')
    parser.add_argument('--only-files-containing-pattern')
    parser.add_argument('url_one', help='[[user@]remote-host:]dir', )
    parser.add_argument('url_two', help='[[user@]remote-host:]dir', )
    args = parser.parse_args()

    tmp_dir_one = create_tmp_dir_and_fill_it_with_files(
        only_files_containing_pattern=args.only_files_containing_pattern,
        url_as_string=args.url_one)
    tmp_dir_two = create_tmp_dir_and_fill_it_with_files(
        only_files_containing_pattern=args.only_files_containing_pattern,
        url_as_string=args.url_two, other_url_as_string=args.url_one)
    diff_command = ['meld', tmp_dir_one, tmp_dir_two]
    logger.info('Calling %s' % diff_command)
    subprocess.call(diff_command)


class CompareURL(object):
    SCHEME_DIR='dir'
    SCHEME_CMD='cmd'

    url = None

    def __init__(self, url):
        url=str(url)
        self.url=url
        self.parsed_url = self.parse_url(self.url)

    @property
    def scheme(self):
        return self.parsed_url['scheme']

    @property
    def user_at_host_or_none(self):
        return self.parsed_url['user_at_host']

    @property
    def directory(self):
        assert self.scheme==self.SCHEME_DIR, self.url
        return self.parsed_url['directory_or_cmd']

    @property
    def command(self):
        assert self.scheme==self.SCHEME_CMD, self.url
        return self.parsed_url['directory_or_cmd']

    _parse_url_regex = r'^((?P<scheme>(cmd|dir):)?(?P<user_at_host>([^@:\s]+@)?[^\s:@]+):)?(?P<directory_or_cmd>.*)$'

    @classmethod
    def parse_url(cls, url):
        match = re.match(cls._parse_url_regex, url)
        scheme = match.groupdict()['scheme']
        if not scheme:
            scheme=cls.SCHEME_DIR
        else:
            scheme=scheme.strip(':')
        directory_or_cmd = match.groupdict()['directory_or_cmd']
        user_at_host = match.groupdict()['user_at_host']
        if scheme==cls.SCHEME_DIR and user_at_host is None and '@' in directory_or_cmd:
            user_at_host = directory_or_cmd
            directory_or_cmd = ''
        return dict(scheme=scheme, user_at_host=user_at_host, directory_or_cmd=directory_or_cmd)

    def add_missing_parts_from_other_url(self, other_url_object):
        if self.parsed_url['directory_or_cmd']:
            return
        self.parsed_url['directory_or_cmd']=other_url_object.parsed_url['directory_or_cmd']

def create_tmp_dir_and_fill_it_with_files(url_as_string, only_files_containing_pattern=None, other_url_as_string=None):
    url_object = CompareURL(url_as_string)
    if other_url_as_string:
        url_object.add_missing_parts_from_other_url(CompareURL(other_url_as_string))

    if url_object.scheme==CompareURL.SCHEME_DIR:
        return create_tmp_dir_and_fill_it_with_files__scheme_dir(url_object, only_files_containing_pattern=only_files_containing_pattern)
    if url_object.scheme==CompareURL.SCHEME_CMD:
        if only_files_containing_pattern:
            raise ValueError('only_files_containing_pattern does not make sense if you use scheme "dir"')
        return create_tmp_dir_and_fill_it_with_files__scheme_cmd(url_object)
    raise ValueError('unsupported scheme %s %s' % (url_object.scheme, url_as_string))

def create_tmp_dir_and_fill_it_with_files__scheme_cmd(url_object):
    cmd = ['ssh', url_object.user_at_host_or_none, url_object.command]
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = pipe.communicate()
    temp_dir = tempfile.mkdtemp(prefix='compare_%s_' % string_to_save_file_name(url_object.url))
    write_output_to_temp_file(temp_dir, stdoutdata, 'stdout')
    write_output_to_temp_file(temp_dir, stderrdata, 'stderr')
    return temp_dir

def write_output_to_temp_file(temp_dir, data, name):
    if not data:
        return
    with io.open(os.path.join(temp_dir, '%s.txt' % name), 'wb') as fd:
        fd.write(data)

def create_tmp_dir_and_fill_it_with_files__scheme_dir(url_object, only_files_containing_pattern=None):

    filter_files_pipe = ''
    if only_files_containing_pattern:
        filter_files_pipe = '''xargs grep -liE '{}' | '''.format(only_files_containing_pattern)
    cmd = []
    shell = True
    if url_object.user_at_host_or_none:
        cmd = ['ssh', url_object.user_at_host_or_none]
        shell = False
    cmd.append('''find "{}" | {} tar --files-from=- -czf- '''.format(
        url_object.directory, filter_files_pipe))
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    (stdoutdata, stderrdata) = pipe.communicate()
    temp_dir = tempfile.mkdtemp(prefix='compare_%s_' % string_to_save_file_name(url_object.url))
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
            try:
                tar_obj.extract(member, str(base_dir))
            except IOError as exc:
                continue


def string_to_save_file_name(my_string):
    return re.sub(r'[^a-zA-Z0-9_@:]', '_', my_string)
