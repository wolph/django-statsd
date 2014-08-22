import os
from setuptools import setup

# Little hack to make sure tests work
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

__package_name__ = 'django-statsd'
__version__ = '1.9.2'
__author__ = 'Rick van Hattem'
__author_email__ = 'Rick.van.Hattem@Fawo.nl'
__description__ = '''django-statsd is a django app that submits query and
    view durations to Etsy's statsd.'''
__url__ = 'https://github.com/WoLpH/django-statsd'

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/django-statsd/'

setup(
    name=__package_name__,
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    url=__url__,
    license='BSD',
    packages=['django_statsd'],
    long_description=long_description,
    test_suite='nose.collector',
    tests_requires='''
        python-statsd
        nose
        git+git://github.com/akheron/nosedjango@nose-and-django-versions#egg=nosedjango
        coverage
        django
        mock
        ''',
    setup_requires=['nose'],
    install_requires=['python-statsd>=1.6.0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
