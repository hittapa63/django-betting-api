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

from mainBet.models import BetChipInformation, UserInformation, BetInformation, Profile, Bet, BetUser, Payment
from mainBet.utils import admin_utils, utils

@method_decorator(login_required, name='dispatch')
class PaymentsView(View):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        context = {}
        context['segment'] = 'payment'
        payments = Payment.objects.order_by('-created_at')
        paginator = Paginator(payments, 10)
        page_obj = paginator.get_page(page_number)
        context['payments'] = page_obj
        html_template = loader.get_template( 'admin-payments.html' )
        return HttpResponse(html_template.render(context, request))

@method_decorator(login_required, name='dispatch')
class PaymentView(View):
    def get(self, request, id):
        context = {}
        html_template = loader.get_template( 'admin-payment.html' )
        return HttpResponse(html_template.render(context, request))

    def post(self, request, id):
        form_data = request.POST
        return redirect('/admin/bets')
