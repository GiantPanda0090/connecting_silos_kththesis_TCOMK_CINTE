from django.conf.urls import url

from . import views

urlpatterns = [
url(r'^$', views.index, name='index'),
url(r'^process$', views.process, name='process'),
url(r'^done$', views.done, name='process'),

]
