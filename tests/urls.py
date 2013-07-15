from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^test_app/$', include('tests.test_app.urls')),
)

