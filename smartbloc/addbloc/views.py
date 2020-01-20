from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def addbloc(request):
    if request.POST:
        print(request.body)
        return HttpResponse(status=200)
    return render(request, "addbloc.html")
