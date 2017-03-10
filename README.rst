compare-with-remote
---------------------

Compare local script output with remote script output

Install
-------

.. code-block:: shell

    pip install -e git+https://github.com/guettli/compare-with-remote.git#egg=compare-with-remote

Usage
-----

.. code-block:: shell

    ===> compare-with-remote -h
    usage: compare-with-remote [-h]
                               [--only-files-containing-pattern ONLY_FILES_CONTAINING_PATTERN]
                               user_at_host file_or_directory
                               [file_or_directory ...]

    compare local files with remote files via ssh. Fetches files via ssh, then
    calls "meld" to copmare the directories

    positional arguments:
      user_at_host          user@remote-host
      file_or_directory

    optional arguments:
      -h, --help            show this help message and exit
      --only-files-containing-pattern ONLY_FILES_CONTAINING_PATTERN
