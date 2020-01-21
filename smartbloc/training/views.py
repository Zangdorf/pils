from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image

import numpy as np

import cv2

from smartbloc.bloc_storage import blocs

import smartbloc.detect_thread as detect_thread

def find_bloc(difficulty):
    filtered = [b for b in blocs if b["difficulty"] == difficulty]
    if len(filtered) <= 0:
        return None
    i = np.random.rand() * (len(filtered) - 1)
    i = int(np.floor(i))
    return filtered[i]

def create_image(circles):
    image = np.ones((1080, 1920, 3), np.uint8)
    for circle in circles:
        cv2.circle(image, (circle["x"], circle["y"]), circle["r"], (255,255,255), 5)
    return image

# Create your views here.
def training(request):
    # img = Image.open('training/static/img/bloc_default.png')
    # img.show()
    
    # close thread if already running
    detect_thread.create_new_thread()

    return render(request, "training.html")

def show(img):
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while True:
        cv2.imshow('window', img)
        key = cv2.waitKey(0)
        print("key:", key)
        if key == 27:
            break
    cv2.destroyAllWindows()

def showImage(request):
    # img = Image.open('training/static/img/bloc_{}.png'.format(request.GET['difficulty']))
    # img = Image.open('training/static/img/test.png')
    bloc = find_bloc(request.GET['difficulty'])
    if bloc:
        img = create_image(bloc["circles"])
        show(img)
    else:
        return HttpResponse(status=405)
    return HttpResponse(status=200)
