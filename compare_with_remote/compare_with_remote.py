# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import argparse
import io
import logging
import os
import subprocess

import sys
import tarfile
import tempfile
from collections import defaultdict

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        description='compare local files with remote files via ssh. Fetches files via ssh, then calls "meld" to copmare the directories. See https://github.com/guettli/compare-with-remote')
    parser.add_argument('--only-files-containing-pattern')
    parser.add_argument('user_at_host', help='user@remote-host', )
    parser.add_argument('file_or_directory_list', nargs='+')
    args = parser.parse_args()
    base_dir = get_base_directory(args.file_or_directory_list)
    tmp_dir_remote = create_tmp_dir_and_fill_it_with_files(
        only_files_containing_pattern=args.only_files_containing_pattern,
        file_or_directory_list_list=args.file_or_directory_list,
        ssh_user_at_host=args.user_at_host)
    files = get_file_list_of_local_directory(tmp_dir_remote)
    if not files:
        raise ValueError('No files found in {}'.format(tmp_dir_remote))
    files = files_to_files_with_base_dir(files, base_dir)
    tmp_dir_local = create_tmp_dir_and_fill_it_with_files(files)
    diff_command = ['meld', tmp_dir_local, tmp_dir_remote]
    logger.info('Calling %s' % diff_command)
    subprocess.call(diff_command)


def get_base_directory(files):
    is_abs = defaultdict(int)
    for file_name in files:
        is_abs[os.path.isabs(file_name)] += 1
    if len(is_abs) > 1:
        raise ValueError('You must not mix relative an absolut paths: %s' % files)
    if is_abs.keys()[0]:
        return '/'
    return '.'


def files_to_files_with_base_dir(files, base_dir):
    tried = []
    ok = False
    for file in files:
        file_with_base_dir = os.path.join(base_dir, file)
        if os.path.exists(file_with_base_dir):
            ok = True
        tried.append(file_with_base_dir)
    if not ok:
        raise Exception('No file of remote was found on the local side. Tried: %s...' % tried[:10])
    return tried


def create_tmp_dir_and_fill_it_with_files(file_or_directory_list_list, only_files_containing_pattern=None,
                                          ssh_user_at_host=None):
    filter_files_pipe = ''
    if only_files_containing_pattern:
        filter_files_pipe = '''xargs grep -liE '{}' | '''.format(only_files_containing_pattern)
    cmd = []
    shell = True
    if ssh_user_at_host:
        cmd = ['ssh', ssh_user_at_host]
        shell = False
    cmd.append('''find {} | {} tar --files-from=- -czf- '''.format(
        ' '.join(["'{}'".format(item) for item in file_or_directory_list_list]),
        filter_files_pipe))
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    (stdoutdata, stderrdata) = pipe.communicate()
    dir_type = ssh_user_at_host or 'local'
    temp_dir = tempfile.mkdtemp(prefix='compare_%s_' % dir_type)
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
    logger.info('{} files were stored in {} {} files {} directories'.format(
        dir_type, temp_dir, file_count, dir_count))
    return temp_dir


def get_file_list_of_local_directory(directory):
    local_files = []
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        local_files.extend([os.path.relpath(os.path.join(root, file_name), directory) for file_name in sorted(files)])
    return local_files

def extract_tar_skip_hard_links(stdoutdata, base_dir):
    # useless reinvention of extractall(). Needed to work around http://bugs.python.org/issue29612
    with tarfile.open(fileobj=io.BytesIO(stdoutdata)) as tar_obj:
        for member in tar_obj.getmembers():
            if member.islnk():
                continue
            tar_obj.extract(member, base_dir)
