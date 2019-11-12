from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image

# Create your views here.
def training(request):
    return render(request, "training.html")

def showImage(request):
    img = Image.open('test.jpg')
    img.show()
    return HttpResponse(status=200)