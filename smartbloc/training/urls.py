from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [

    url(r'^$', views.training, name='training'),
    path('showImage', views.showImage),

]