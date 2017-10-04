from django.shortcuts import render

# Create your views here.
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from Project.forms import SignUpForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.views import View
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import logout
import datetime


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()

            messages.add_message(request, messages.INFO, "New User is created. Please Login")

            return HttpResponseRedirect(reverse("home"))
        else:
            form = SignUpForm(request.POST)
    else:
        form =SignUpForm()

    return render(request,"register.html", {'form': form})

@method_decorator(login_required)

def createbid(request):
    if request.method == 'POST' and user.is_active:
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("createbid"))


