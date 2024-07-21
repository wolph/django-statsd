from django import urls

urlpatterns = [
    urls.re_path(r'^test_app/$', urls.include('tests.test_app.urls')),
]
