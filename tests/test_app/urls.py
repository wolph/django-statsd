from django import urls
from . import views

urlpatterns = [
    urls.path(r'', views.index, name='index'),
]
