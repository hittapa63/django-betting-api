from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import datetime
from django.contrib.auth import authenticate, logout, login, logout
from .forms import LoginForm, SignUpForm
from django.shortcuts import render, redirect

from mainBet.utils import utils
from mainBet.models import Profile, Bet, Payment, BetUser

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None and user.is_superuser is True:
                login(request, user)
                return redirect("/admin")
            else:    
                msg = 'Invalid credentials'    
        else:
            msg = 'Error validating the form'    

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def logout_view(request):
    logout(request)
    return redirect('/admin/login')