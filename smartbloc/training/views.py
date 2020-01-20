from django.shortcuts import render
from django.http import HttpResponse
from PIL import Image

# Create your views here.
def training(request):
    # img = Image.open('training/static/img/bloc_default.png')
    # img.show()
    return render(request, "training.html")

def showImage(request):
    print(request.GET)
    # img = Image.open('training/static/img/bloc_{}.png'.format(request.GET['difficulty']))
    img = Image.open('training/static/img/test.png')
    img.show()
    return HttpResponse(status=200)
