import os
from setuptools import setup, find_packages

# Little hack to make sure tests work
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

import django_statsd

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/django-statsd/'

version = '1.8.1'
setup(
    name='django-statsd',
    version=version,
    author='Rick van Hattem',
    author_email='Rick.van.Hattem@Fawo.nl',
    description='''django-statsd is a django app that submits query and 
        view durations to Etsy's statsd.''',
    url='https://github.com/WoLpH/django-statsd',
    license='BSD',
    packages=['django_statsd'],
    long_description=long_description,
    test_suite='nose.collector',
    tests_requires=[
        'nose',
        'gitt+git://github.com/akheron/nosedjango@nose-and-django-versions#egg=nosedjango',
        'coverage',
        'django',
        'mock',
    ],
    setup_requires=['nose'],
    install_requires=['python-statsd>=1.5.1'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
