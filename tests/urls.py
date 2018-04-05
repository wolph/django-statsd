from django.conf import urls

urlpatterns = [
    urls.url(r'^test_app/$', urls.include('tests.test_app.urls')),
]
