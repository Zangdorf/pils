from django.conf.urls import url
from . import views

urlpatterns = [

    url('', views.cover, name='cover'),
    url(r'cover/$', views.cover, name='cover'),
]