from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.models import model_to_dict

from .forms import RegisterForm, LoginForm
from .models import User

from . import settings

import json

import numpy as np
import urllib
import cv2

# Create your views here.
def cover(request):
    return render(request, "cover.html")

def register(request):
    if request.POST:
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            if User.is_email_taken(data['email']):
                form.add_error('email', 'Email déjà utilisée')
                return render(request, 'register.html', {'form': form})

            user = User(email=data['email'], password=data['password'])
            user.save()

            return HttpResponseRedirect('/login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            queryset = User.objects.filter(email=data['email'], password=data['password'])
            if len(queryset) >= 1:
                user = queryset[0]
                request.session['user'] = model_to_dict(user)

                return HttpResponseRedirect('/')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout(request):
    request.session['user'] = None
    return HttpResponseRedirect('/')

def calibrate(request):
    print("CALIBRATE")
    if request.POST:
        settings.CAMERA_MARGIN_BOTTOM = int(request.POST["marginBottom"])
        settings.CAMERA_MARGIN_TOP = int(request.POST["marginTop"])
        return HttpResponse(status=200)
    else:
        return render(request, 'calibrate.html', {
                'camera_url': settings.CAMERA_URL + '/video',
            'top_margin': settings.CAMERA_MARGIN_TOP,
            'bottom_margin': settings.CAMERA_MARGIN_BOTTOM
        })

def calibrate_image(request):
    resp = urllib.request.urlopen(settings.CAMERA_URL + '/shot.jpg')
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    (h, w) = image.shape[0:2]

    cv2.rectangle(image, (0, 0), (w, settings.CAMERA_MARGIN_TOP), (255,0,0), 2)
    cv2.rectangle(image, (0, h - settings.CAMERA_MARGIN_BOTTOM), (w, h), (255,0,0), 2)

    _, image = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

    return HttpResponse(image.tostring(), content_type="image/jpg")
