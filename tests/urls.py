from django import urls

from tests import views

urlpatterns = [
    urls.path('', views.index, name='index'),
    urls.path('db/', views.db_query, name='db_query'),
    urls.path('error/', views.error, name='error'),
    urls.path('template/', views.template, name='template'),
]
