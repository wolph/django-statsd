from django.conf import urls

urlpatterns = urls.patterns('views',
    urls.url(r'^$', 'index', name='index'),
)

