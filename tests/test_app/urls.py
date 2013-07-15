from django.conf import urls

urlpatterns = urls.patterns('tests.test_app.views',
    urls.url(r'^$', 'index', name='index'),
)

