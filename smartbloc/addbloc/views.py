from django.shortcuts import render
from django.http import HttpResponse

import json

from smartbloc.bloc_storage import blocs

# Create your views here.
def addbloc(request):
    if request.method == "POST":
        new_bloc = json.loads(request.body)
        blocs.append(new_bloc)
        return HttpResponse(status=200)
    return render(request, "addbloc.html")
