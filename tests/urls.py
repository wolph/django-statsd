try:
    from django.urls import re_path as url, include
except ImportError:
    from django.conf.urls import url, include

urlpatterns = [
    url(r'^test_app/$', include('tests.test_app.urls')),
]

try:
    from django.conf.urls import patterns
    urlpatterns = patterns('', urlpatterns)
except ImportError:
    pass
