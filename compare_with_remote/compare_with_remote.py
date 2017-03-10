# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals, print_function

import argparse
import io
import logging
import os
import subprocess
import tarfile
import tempfile

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='compare local files with remote files via ssh')
    parser.add_argument('--only-files-containing-pattern')
    parser.add_argument('user_at_host', help='user@remote-host', )
    parser.add_argument('file_or_directory', nargs='+')
    args = parser.parse_args()
    tmp_dir_remote = create_tmp_dir_and_fill_it_with_files(
        only_files_containing_pattern=args.only_files_containing_pattern,
        file_or_directory_list=args.file_or_directory,
        ssh_user_at_host=args.user_at_host)
    files = get_file_list_of_local_directory(tmp_dir_remote)
    check_if_local_files_exist(files)
    tmp_dir_local = create_tmp_dir_and_fill_it_with_files(files)
    diff_command=['meld', tmp_dir_local, tmp_dir_remote]
    logger.info('Calling %s' % diff_command)
    subprocess.call(diff_command)


def check_if_local_files_exist(files):
    for file in files:
        if os.path.exists(file):
            return True
    raise Exception('No file of remote was found on the local side. Tried: %s...' % files[:10])

def create_tmp_dir_and_fill_it_with_files(file_or_directory_list, only_files_containing_pattern=None,
                                          ssh_user_at_host=None):
    filter_files_pipe = ''
    if only_files_containing_pattern:
        filter_files_pipe = '''| xargs grep -liE '{}' '''.format(only_files_containing_pattern)
    cmd = []
    shell=True
    if ssh_user_at_host:
        cmd = ['ssh', ssh_user_at_host]
        shell = False
    cmd.append('''find {} | {} tar --files-from=- -czf- '''.format(
        ' '.join(["'{}'".format(item) for item in file_or_directory_list]),
        filter_files_pipe))
    print('#################### %s' % cmd)
    pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
    (stdoutdata, stderrdata) = pipe.communicate()
    dir_type = ssh_user_at_host or 'local'
    temp_dir = tempfile.mkdtemp(prefix='compare_%s_' % dir_type)
    tar = tarfile.open(fileobj=io.BytesIO(stdoutdata))
    tar.extractall(temp_dir)
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
