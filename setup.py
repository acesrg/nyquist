import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="nyquist",
    version="0.2.4",
    author="Marco Miretti",
    author_email="marcomiretti@gmail.com",
    description=("A client for control-systems laboratories."),
    license="GPLv3",
    keywords="control laboratories remote client http websockets",
    url="http://packages.python.org/nyquist",
    packages=[
        'nyquist.{}'.format(sub_pkg) for sub_pkg in find_packages(
            where='src/nyquist'
        )
    ],
    package_dir={'': 'src'},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
)
