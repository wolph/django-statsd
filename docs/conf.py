"""Sphinx configuration for django-statsd."""

import os
import sys
from importlib import metadata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

import django  # noqa: E402

django.setup()

project = 'django-statsd'
author = 'Rick van Hattem (Wolph)'
copyright = '2012-2026, Rick van Hattem (Wolph)'
release = metadata.version('django-statsd')
version = '.'.join(release.split('.')[:2])

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}
exclude_patterns = ['_build']
html_theme = 'furo'
