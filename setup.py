import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-statsd',
    version = '1.1',
    author = 'Rick van Hattem',
    author_email = 'Rick.van.Hattem@Fawo.nl',
    description = '''django-statsd is a django app that submits query and 
        view durations to Etsy's statsd.''',
    url='https://github.com/WoLpH/django-statsd',
    license = 'BSD',
    packages=['django_statsd'],
    long_description=read('README.rst'),
    test_suite='nose.collector',
    setup_requires=['nose'],
    tests_require=['django'],
    install_requires=['python-statsd'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
    ],
)
