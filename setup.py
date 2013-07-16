import os
from setuptools import setup, find_packages

# Little hack to make sure tests work
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

import django_statsd

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/django-statsd/'

setup(
    name=django_statsd.__name__,
    version=django_statsd.__version__,
    author=django_statsd.__author__,
    author_email=django_statsd.__author_email__,
    description=django_statsd.__description__,
    url=django_statsd.__url__,
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
    install_requires=['python-statsd>=1.6.0'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
