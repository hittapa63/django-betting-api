from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
import datetime

from mainBet.models import BetChipInformation, UserInformation, BetInformation, Profile, Bet

@login_required
def index(request):

    year = datetime.datetime.today().year
    context = {}
    context['segment'] = 'index'
    context['user_info'] = UserInformation.objects.filter(year=year).order_by('-created_at')
    context['bet_info'] = BetInformation.objects.filter(year=year).order_by('-created_at')
    context['bet_chip_info'] = BetChipInformation.objects.filter(year=year).order_by('-created_at')
    context['top_users'] = Profile.objects.order_by('-exp')[:6]
    recent_bets = Bet.objects.order_by('-created_at')[:6]
    listset = [x.as_dict() for x in recent_bets]
    context['recent_bets'] = listset

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))

def handle_not_found(request, exception):
    return render(request, '404.html')
