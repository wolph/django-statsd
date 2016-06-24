import os
import setuptools

__package_name__ = 'django-statsd'
__version__ = '2.1.1'
__author__ = 'Rick van Hattem'
__author_email__ = 'Rick.van.Hattem@Fawo.nl'
__description__ = '''django-statsd is a django app that submits query and
    view durations to Etsy's statsd.'''
__url__ = 'https://github.com/WoLpH/django-statsd'

if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = 'See http://pypi.python.org/pypi/%s/' % (
        __package_name__)


if __name__ == '__main__':
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
        tests_require=[
            'pytest',
            'pytest-cache',
            'pytest-cov',
            'pytest-django',
            'flake8',
            'django<1.6',
            'mock',
        ],
        setup_requires=['setuptools', 'pytest-runner'],
        install_requires=['python-statsd>=1.7.2'],
        classifiers=[
            'License :: OSI Approved :: BSD License',
        ],
    )

