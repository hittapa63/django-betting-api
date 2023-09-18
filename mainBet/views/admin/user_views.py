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

from mainBet.models import BetChipInformation, UserInformation, BetInformation, Profile, Bet
from mainBet.utils import admin_utils, utils

@method_decorator(login_required, name='dispatch')
class UsersView(View):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        try:
            status = int(request.GET.get('status'))
        except:
            status = None
        context = {}
        context['segment'] = 'user'
        if status is None:
            users = Profile.objects.order_by('-created_at')
        else:
            users = Profile.objects.filter(status=status).order_by('-created_at')
        info = {
            'total': Profile.objects.count(),
            'active': Profile.objects.filter(status=1).count(),
            'deactive': Profile.objects.filter(status=0).count(),
            'bets': Profile.objects.filter(~Q(bets=0)).count()
        }
        context['info']= info
        paginator = Paginator(users, 15)
        page_obj = paginator.get_page(page_number)
        context['users'] = page_obj
        context['status'] = status
        html_template = loader.get_template( 'admin-users.html' )
        return HttpResponse(html_template.render(context, request))

    def post(self, request):
        form_data = request.POST
        # user added part.

    def put(self, request):
        form_data = QueryDict(request.body)
        status = form_data.get('status', None)
        profile_id = form_data.get('profile_id', None)
        profile = Profile.objects.filter(pk=profile_id).first()
        if profile is None:
            return admin_utils.admin_json_response(304, None, 'There is no User!')
        else:
            profile.status = int(status)
            profile.save()
            admin_utils.record_user_information(profile, is_new=False)    
            profile_info = model_to_dict(profile, fields=['user', 'address', 'fcm_token', 'winner_times', 'tie_times', 'lose_times', 'provider_id', 'social_type', 'photo', 'chip', 'exp', 'timezone', 'status'])
            info = profile_info
            return admin_utils.admin_json_response(200, [info], 'Successfully User Status updated!')

@method_decorator(login_required, name='dispatch')
class UserView(View):
    def get(self, request, id):
        user = User.objects.filter(pk=id).first()
        profile = None
        if user != None:
            profile = Profile.objects.filter(user= user).first()
        context = {}
        context['segment'] = 'user'
        context['user'] = profile
        html_template = loader.get_template( 'admin-user.html' )
        return HttpResponse(html_template.render(context, request))

    def post(self, request, id):
        form_data = request.POST
        fs = FileSystemStorage()
        username = form_data.get('username', None)
        email = form_data.get('email', None)
        first_name = form_data.get('first_name', 'first_name')
        last_name = form_data.get('last_name', 'last_name')
        address = form_data.get('address', None)
        bets = form_data.get('bets', 0)
        exp = form_data.get('exp', 0)
        chip = form_data.get('chip', 0)
        winner_times = form_data.get('winner_times', 0)
        tie_times = form_data.get('tie_times', 0)
        lose_times = form_data.get('lose_times', 0)
        photo = form_data.get('photo', None)
        user = User.objects.filter(pk= id).first()
        profile = Profile.objects.filter(user = user).first()
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        profile.address = address
        profile.bets = bets
        profile.exp = exp
        profile.chip = chip
        profile.winner_times = winner_times
        profile.tie_times = tie_times
        profile.lose_times = lose_times
        if photo != None and photo != '' and ';base64,' in photo:
            format, imgstr = photo.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr))  
            file_name = str(datetime.datetime.now().timestamp()) + '.' +ext
            filename = fs.save(file_name, data)
            uploaded_file_url = fs.url(filename)
            filepath = utils.get_domain(request) + '/static' + uploaded_file_url
            profile.photo = filepath
        profile.save()
        return redirect('/admin/users')
