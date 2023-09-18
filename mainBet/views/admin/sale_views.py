from django.template import loader
from django.http import HttpResponse, JsonResponse
from django import template
import datetime
from django.views import View
from django.core.paginator import Paginator
from django.http import QueryDict
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from mainBet.models import BetChipInformation, UserInformation, BetInformation, Profile, Bet, BetUser
from mainBet.utils import admin_utils, utils

@method_decorator(login_required, name='dispatch')
class SalesView(View):
    def get(self, request):
        year = datetime.datetime.today().year
        context = {}
        context['segment'] = 'sale'
        context['bet_chip_info'] = BetChipInformation.objects.filter(year=year).order_by('-created_at')
        info = {
            'total_users': Profile.objects.filter(~Q(status=2)).count(),
            'total_bets' : Bet.objects.count(),
            'bets_users' : round(Bet.objects.count()/Profile.objects.filter(~Q(status=2)).count(), 2),
            'total_winers' : BetUser.objects.filter(is_winner=True).count(),
            'total_losers' : BetUser.objects.filter(is_winner=False).count(),
            'total_tiers' : BetUser.objects.filter(is_winner=None).count()
        }
        context['info']= info
        html_template = loader.get_template( 'admin-sales.html' )
        return HttpResponse(html_template.render(context, request))

@method_decorator(login_required, name='dispatch')
class SaleView(View):
    def get(self, request, id):
        context = {}
        html_template = loader.get_template( 'admin-bet.html' )
        return HttpResponse(html_template.render(context, request))

    def post(self, request, id):
        form_data = request.POST
        return redirect('/admin/bets')
