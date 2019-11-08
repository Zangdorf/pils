from django.shortcuts import render

# Create your views here.
def stats(request):
    return render(request, "stats.html")
