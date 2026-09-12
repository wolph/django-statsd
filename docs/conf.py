"""Sphinx configuration for django-statsd."""

import os
import sys
from importlib import metadata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

import django  # noqa: E402

django.setup()

# -- Project information
project = 'django-statsd'
author = 'Rick van Hattem (Wolph)'
copyright = '2012-2026, Rick van Hattem (Wolph)'
release = metadata.version('django-statsd')
version = '.'.join(release.split('.')[:2])

# -- Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# -- Theme
html_theme = 'furo'

# -- Napoleon (Google-style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'django': (
        'https://docs.djangoproject.com/en/stable/',
        'https://docs.djangoproject.com/en/stable/_objects/',
    ),
}

# -- Autodoc
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

exclude_patterns = ['_build']
