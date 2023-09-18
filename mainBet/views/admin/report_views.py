from django.template import loader
from django.http import HttpResponse, JsonResponse
from django import template
import datetime
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
import base64
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
class ReportUsersView(View):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        context = {}
        context['segment'] = 'report'
        users = Profile.objects.order_by('-created_at')
        paginator = Paginator(users, 24)
        page_obj = paginator.get_page(page_number)
        context['users'] = page_obj
        html_template = loader.get_template( 'admin-reports-users.html' )
        return HttpResponse(html_template.render(context, request))

@method_decorator(login_required, name='dispatch')
class ReportUserView(View):
    def get(self, request, id):
        user = User.objects.filter(pk=id).first()
        profile = None
        if user != None:
            profile = Profile.objects.filter(user= user).first()
        context = {}
        context['segment'] = 'report'
        context['user'] = profile
        context['bets'] = Bet.objects.filter(creator=profile).order_by('-created_at')
        context['bet_users'] = BetUser.objects.filter(user=profile).order_by('-created_at')
        html_template = loader.get_template( 'admin-reports-user.html' )
        return HttpResponse(html_template.render(context, request))
