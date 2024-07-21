from django import urls

from . import views

urlpatterns = [
    urls.re_path(r'^$', views.index, name='index'),
]
