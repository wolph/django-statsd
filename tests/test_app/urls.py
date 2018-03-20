try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url


from tests.test_app.views import index
urlpatterns = [
    url(r'^$', index, name='index'),
]

try:
    from django.conf.urls import patterns
    urlpatterns = patterns('', urlpatterns)
except ImportError:
    pass
