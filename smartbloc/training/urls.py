from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [

    url(r'^$', views.training, name='training'),
    path('showImage', views.show_image),
    path('status', views.training_status),

]