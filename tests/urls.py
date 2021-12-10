from django import urls

urlpatterns = [
    urls.path('test_app/', urls.include('tests.test_app.urls')),
]
