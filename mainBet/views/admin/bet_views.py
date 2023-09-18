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
class BetsView(View):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        try:
            status = int(request.GET.get('status'))
        except:
            status = None
        try:
            is_active = int(request.GET.get('is_active'))
        except:
            is_active = None
        try:
            is_opened = int(request.GET.get('is_opened'))
        except:
            is_opened = None
        context = {}
        context['segment'] = 'bet'
        if status is None:
            bets = Bet.objects.order_by('-created_at')
        else:
            if is_active is None and is_opened is None:
                bets = Bet.objects.filter(status=status).order_by('-created_at')
            else:
                if is_active is None:
                    bets = Bet.objects.filter(status=status, is_opened=is_opened).order_by('-created_at')
                elif is_opened is None:
                    bets = Bet.objects.filter(status=status, is_active=is_active).order_by('-created_at')
                else:
                    bets = Bet.objects.filter(status=status, is_active=is_active, is_opened=is_opened).order_by('-created_at')
        info = {
            'total': Bet.objects.count(),
            'open': Bet.objects.filter(is_opened=True, status=1).count(),
            'active': Bet.objects.filter(is_active=True, status=1).count(),
            'deactive': Bet.objects.filter(status=0).count(),
            'untie': Bet.objects.filter(~Q(winner_artist=0)).filter(is_active=False).count(),
            'tie': Bet.objects.filter(is_active=False, winner_artist=0).count(),
            'winner': BetUser.objects.filter(is_end=True, is_winner=True).count(),
            'loser': BetUser.objects.filter(is_end=True, is_winner=False).count(),
            'tier': BetUser.objects.filter(is_end=True, is_winner=None).count(),
        }
        context['info']= info
        paginator = Paginator(bets, 10)
        page_obj = paginator.get_page(page_number)
        context['bets'] = page_obj
        context['status'] = status
        context['is_active'] = is_active
        context['is_opened'] = is_opened
        html_template = loader.get_template( 'admin-bets.html' )
        return HttpResponse(html_template.render(context, request))

    def post(self, request):
        form_data = request.POST
        # bet added part.

    def put(self, request):
        form_data = QueryDict(request.body)
        status = form_data.get('status', None)
        bet_id = form_data.get('bet_id', None)
        bet = Bet.objects.filter(pk=bet_id).first()
        if bet is None:
            return admin_utils.admin_json_response(304, None, 'There is no bet!')
        else:
            bet.status = int(status)
            bet.save()
            return admin_utils.admin_json_response(200, [bet.as_dict()], 'Successfully Bet Status updated!')

@method_decorator(login_required, name='dispatch')
class BetView(View):
    def get(self, request, id):
        bet = Bet.objects.filter(pk=id).first()
        bet_users = None
        if bet != None:
            bet_users = BetUser.objects.filter(bet=bet)
        context = {}
        context['segment'] = 'bet'
        context['bet'] = bet
        context['bet_users'] = bet_users
        html_template = loader.get_template( 'admin-bet.html' )
        return HttpResponse(html_template.render(context, request))

    def post(self, request, id):
        form_data = request.POST
        return redirect('/admin/bets')
