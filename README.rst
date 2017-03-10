compare-with-remote
---------------------

Compare local files with remote files 

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

Context
-------

This is a generic file comparing tool. I wrote it to help the transition from "pet to cattle". With other words
I am switching from linux server managed with vi and ssh to configuration management.

Examples
--------

You want to compare all files in the /etc directory which contain the word "rsyslog":

.. code-block:: shell

    root@local-server> compare-with-remote --only-files-containing-pattern rsyslog remote-server /etc


Don't be shy
------------

I want to know what you think and feel. Please leave a comment via the github issue tracker. I love feedback.
