from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict

from .forms import RegisterForm, LoginForm
from .models import User

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
