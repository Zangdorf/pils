from django.shortcuts import render

# Create your views here.
def compet(request):
    return render(request, "compet.html")