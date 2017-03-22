import setuptools
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='compare-with-remote',

    version='0.2.0',

    description=' Compare local script output with remote script output',
    long_description=long_description,

    url='https://github.com/guettli/compare-with-remote/',

    author='Thomas Guettler',
    author_email='info.compare-with-remote@thomas-guettler.de',

    license='Apache2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache2',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    packages=setuptools.find_packages(),

    entry_points={
        'console_scripts': [
            'compare-with-remote=compare_with_remote.compare_with_remote:main',
        ],
    },
)
