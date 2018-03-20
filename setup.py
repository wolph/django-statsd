import os
import sys
from setuptools.command.test import test as TestCommand

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


# To prevent importing about and thereby breaking the coverage info we use this
# exec hack
about = {}
with open('django_statsd/__about__.py') as fp:
    exec(fp.read(), about)


if os.path.isfile('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = \
        'See http://pypi.python.org/pypi/%(__package_name__)s/' % about


tests_require = [
    'pytest',
    'pytest-cache',
    'pytest-cov',
    'pytest-django',
    'flake8',
    'django',
    'mock',
]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        import shlex
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


if __name__ == '__main__':
    setup(
        name=about['__package_name__'],
        version=about['__version__'],
        author=about['__author__'],
        author_email=about['__email__'],
        description=about['__description__'],
        url=about['__url__'],
        license='BSD',
        packages=find_packages(exclude=[
            'tests',
            'tests.*',
        ]),
        long_description=long_description,
        tests_require=tests_require,
        extras_require=dict(
            docs=[
                'sphinx',
            ],
            tests=tests_require,
        ),
        setup_requires=[
            'setuptools',
        ],
        install_requires=[
            'python-statsd>=1.7.2',
            'django',
        ],
        cmdclass={'test': PyTest},
        classifiers=[
            'License :: OSI Approved :: BSD License',
        ],
    )

