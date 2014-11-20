import os
import sys
import setuptools

__package_name__ = 'django-statsd'
__version__ = '2.0.0'
__author__ = 'Rick van Hattem'
__author_email__ = 'Rick.van.Hattem@Fawo.nl'
__description__ = '''django-statsd is a django app that submits query and
    view durations to Etsy's statsd.'''
__url__ = 'https://github.com/WoLpH/django-statsd'

from setuptools.command.test import test as TestCommand
if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/%s/' % (
        __package_name__)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setuptools.setup(
    name=__package_name__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    url=__url__,
    license='BSD',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    long_description=long_description,
    cmdclass={'test': PyTest},
    install_requires=['python-statsd>=1.6.0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)

