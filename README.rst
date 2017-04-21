.. image:: https://travis-ci.org/guettli/compare-with-remote.svg?branch=master
    :target: https://travis-ci.org/guettli/compare-with-remote


compare-with-remote
---------------------

Compare local files with remote files 

About
-----

This is a generic file comparing tool. I wrote it to help the transition from "pet to cattle". With other words
I am switching from linux server managed with vi and ssh to configuration management.

It helps you to compare files on a remote host with files on your local file system.

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
                               directory_url_one directory_url_two

    compare two directories. Directories can get fetched via ssh first, then
    "meld" get called to copmare the directories. See https://github.com/guettli
    /compare-with-remote

    positional arguments:
      directory_url_one     [[user@]remote-host:]dir
      directory_url_two     [[user@]remote-host:]dir

    optional arguments:
      -h, --help            show this help message and exit
      --only-files-containing-pattern ONLY_FILES_CONTAINING_PATTERN


Examples
--------

You want to compare all files in the /etc directory which contain the word "rsyslog":

.. code-block:: shell

    root@local-server> compare-with-remote --only-files-containing-pattern rsyslog \
                                              root@server-with-cute-name-1:/etc \
                                              root@server-with-cute-name-2:/etc

You can compare the output of scripts like this:

.. code-block:: shell

    root@local-server> compare-with-remote \
        'postgres@server-with-cute-name-1:psql -c "select app, name from django_migrations order by id"' \
        'postgres@server-with-cute-name-2:'

If you don't provide a remote-command for the second host, then the command from the first host will get called. In this case
all rows of a database table get compared.


Screenshots
-----------

After fetching the files, the script calls the tool "meld" to show the actual diff:

.. image:: https://github.com/guettli/compare-with-remote/blob/master/docs/screenshot-of-meld-compare-directory.png


Here is a screenshot of meld showing the difference between two files:

.. image:: https://github.com/guettli/compare-with-remote/blob/master/docs/screenshot-of-meld-compare-file.png

Don't be shy
------------

I want to know what you think and feel. Please leave a comment via the github issue tracker. I love feedback.
