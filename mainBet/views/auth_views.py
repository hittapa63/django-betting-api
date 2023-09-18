from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, logout, login
import random
import datetime

from mainBet.utils import utils, admin_utils
from mainBet.models import Profile, VerifyCode
from mainBet.views import firebase_views

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form_data = request.POST
        valdator = utils.register_validation(form_data)
        if valdator['status'] == False:
            return utils.api_json_response(304, valdator['data'])
        username = form_data.get('username')
        password = form_data.get('password')
        first_name = form_data.get('first_name', 'first_name')
        last_name = form_data.get('last_name', 'last_name')
        email = form_data.get('email')
        address = form_data.get('address', None)
        provider_id = form_data.get('provider_id', None)
        social_type = form_data.get('social_type', None)
        timezone = form_data.get('timezone', None)
        # birth_date = form_data.get('birth_date', None)
        user = User.objects.create(
            username = username,
            email = email,
            first_name = first_name,
            last_name = last_name
        )
        user.set_password(password)
        user.save()
        token = utils.generate_token(user.pk, 10)
        profile = Profile.objects.create(
            user = user,
            token = token,
            address = address,
            provider_id = provider_id,
            social_type = social_type,
            timezone = timezone,
            # birth_date = birth_date
        )
        admin_utils.record_user_information(profile, is_new=True)
        user_info = model_to_dict(user, fields=['pk', 'email', 'username'])
        profile_info = model_to_dict(profile, fields=['user', 'address', 'token','firebase_uid', 'provider_id', 'social_type', 'photo', 'chip', 'exp', 'timezone', 'created_at', 'updated_at'])
        info = user_info | profile_info
        return utils.api_json_response(200, [info])
    else:
        return utils.api_json_response(400, 'Invalid Request')

@csrf_exempt
def sign_in(request):
    if request.method == 'POST':
        form_data = request.POST
        password = form_data.get('password')
        email = form_data.get('email')
        timezone = form_data.get('timezone', None)
        request_user = User.objects.filter(email = email).first()
        if request_user:
            user = authenticate(request, username = request_user.username, password = password)
            if user is not None:
                token = utils.generate_token(user.pk, 10)
                Profile.objects.filter(user = user).update(token=token)
                profile = Profile.objects.filter(user = user).first()
                profile.timezone = timezone
                profile.save()
                if profile.status != 1:
                    return utils.api_json_response(304, 'Your account is blocked. Please contact OkBet Manager.')
                user_info = model_to_dict(user, fields=['pk', 'email', 'username', 'first_name', 'last_name'])
                profile_info = model_to_dict(profile, fields=['user', 'address', 'token','firebase_uid', 'provider_id', 'social_type', 'photo', 'chip', 'exp', 'timezone', 'created_at', 'updated_at'])
                info = user_info | profile_info
                return utils.api_json_response(200, [info])
            else:
                return utils.api_json_response(304, 'Wrong password')
        else:
            return utils.api_json_response(304, 'Unregistered email.')
    else:
        return utils.api_json_response(400, 'Invalid Request')

@csrf_exempt
def social_login(request):
    if request.method == 'POST':
        form_data = request.POST
        email = form_data.get('email', None)
        firebase_uid = form_data.get('firebase_uid', None)
        provider_id = form_data.get('provider_id', None)
        social_type = form_data.get('social_type', None)
        id_token = form_data.get('id_token', None)
        timezone = form_data.get('timezone', None)
        if email == None or firebase_uid == None or provider_id == None or social_type ==None or id_token==None:
            return utils.api_json_response(304, 'Feilds Required.')
        firebase_user = firebase_views.get_user_info_with_uid(firebase_uid)
        if firebase_user == None:
            return utils.api_json_response(304, 'No exist.')
        print(firebase_user.uid)
        print(firebase_user.email)
        print(firebase_user.photo_url)
        if email != firebase_user.email or firebase_uid != firebase_user.uid:
            return utils.api_json_response(304, 'Your account does not match in our database.')
        user = User.objects.filter(email = email).first()
        if user == None:
            user = User.objects.create(
                username = firebase_uid,
                email = email,
                first_name = 'first_name',
                last_name = 'last_name'
            )
            user.set_password('password')
            user.save()
            token = utils.generate_token(user.pk, 10)
            profile = Profile.objects.create(
                user = user,
                token = token,
                firebase_uid = firebase_uid,
                provider_id = provider_id,
                social_type = social_type,
                timezone = timezone,
                photo = firebase_user.photo_url
                # birth_date = birth_date
            )
        else:
            profile = Profile.objects.filter(user = user).first()
            if profile.firebase_uid != firebase_uid:
                return utils.api_json_response(304, 'Your email info is already by another in our service.')
            else:
                token = utils.generate_token(user.pk, 10)
                Profile.objects.filter(user = user).update(token=token)
                profile = Profile.objects.filter(user = user).first()
                profile.timezone = timezone
                profile.save()
        user_info = model_to_dict(user, fields=['pk', 'email', 'username'])
        profile_info = model_to_dict(profile, fields=['user', 'address', 'token', 'firebase_uid' ,'provider_id', 'social_type', 'photo', 'chip', 'exp', 'timezone', 'created_at', 'updated_at'])
        info = user_info | profile_info
        return utils.api_json_response(200, [info])
    else:
        return utils.api_json_response(304, 'Invalid Request.')

@csrf_exempt
def update(request):
    if request.method == 'POST':
        form_data = request.POST
        user = User.objects.filter(pk=request.GET.get('uid')).first()
        profile = Profile.objects.filter(user = user).first()
        email = form_data.get('email', user.email)
        username = form_data.get('username', user.username)
        first_name = form_data.get('first_name', user.first_name)
        last_name = form_data.get('last_name', user.last_name)
        address = form_data.get('address', profile.address)
        fcm_token = form_data.get('fcm_token', profile.fcm_token)
        if email != user.email:
            user = User.objects.filter(email = email).first()
            return utils.api_json_response(304, 'This email is already registered in our service.')
        if username != user.username:
            user = User.objects.filter(username = username).first()
            return utils.api_json_response(304, 'This username is already registered in our service.')
        user.email = email
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        profile.address = address
        profile.fcm_token = fcm_token
        profile.updated_at = datetime.datetime.now()
        user.save()
        profile.save()
    else:
        return utils.api_json_response(400, 'Invalid Request')

@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        form_data = request.POST
        old_password = form_data.get('old_password', None)
        new_password = form_data.get('new_password', None)
        if new_password == None:
            return utils.api_json_response(304, 'New password Required.')
        request_user = User.objects.get(id=request.GET.get('uid'))
        if request_user:
            user = authenticate(request, username = request_user.username, password = old_password)
            if user is not None:
                user.set_password(new_password)
                user.save()
                return utils.api_json_response(200, 'Successfully password changed.')
            else:
                return utils.api_json_response(304, 'Please confirm the old password.')
        else:
            return utils.api_json_response(304, 'Unregistered user.')
    else:
        return utils.api_json_response(400, 'Invalid Request')

# forgot password request with email
# send the email to use after generating the verify code.
# currenlty, user can attempt the 3 times to one verify code.
# also, the verify code is existed for 30 minutes after generating.
@csrf_exempt
def request_forgot_password(request):
    if request.method == 'POST':
        form_data = request.POST
        email = form_data.get('email', None)
        request_user = User.objects.filter(email = email).first()
        if request_user:
            code = random.randint(100000, 999999)
            verify_code = VerifyCode.objects.create(
                email = email,
                code = code
            )
            # In here, need to send email using sendgrid
            # need to ask the sendgrid account to get sendgrid key.
            return utils.api_json_response(200, 'Please verify your email to get the verify code.')
        else:
            return utils.api_json_response(304, 'Unregistered user.')
    else:
        return utils.api_json_response(400, 'Invalid Request')

# check the verify code.
# see the above description request_forgot_password function.
@csrf_exempt
def verify_code(request):
    if request.method == 'POST':
        form_data = request.POST
        email = form_data.get('email', None)
        code = int(form_data.get('verify_code', 0))
        verify_code = VerifyCode.objects.filter(email = email).first()
        if verify_code:
            stand_time = datetime.datetime.now() - datetime.timedelta(minutes=30)
            if stand_time.timestamp() > verify_code.created_at.timestamp():
                verify_code.delete()
                return utils.api_json_response(304, 'Your verify code was expired. Please use another verify code.')
            if verify_code.code != code:
                verify_code.attempts = verify_code.attempts+1
                if verify_code.attempts >= 3:
                    verify_code.delete()
                    return utils.api_json_response(304, 'Too many attempts with wrong code. Please use another verify code.')
                else:
                    verify_code.save()
                    return utils.api_json_response(304, 'Your verify code is wrong. Please input correct code.')
            else:
                verify_code.delete()
                return utils.api_json_response(200, 'Successfully verified.')
        else:
            return utils.api_json_response(304, 'Unregistered code in our server.')
    else:
        return utils.api_json_response(400, 'Invalid Request')

#set password after verifying the code.
@csrf_exempt
def set_password(request):
    if request.method == 'POST':
        form_data = request.POST
        email = form_data.get('email', None)
        new_password = form_data.get('password', None)
        if new_password == None or email == None:
            return utils.api_json_response(304, 'Required Fields')
        request_user = User.objects.filter(email = email).first()
        if request_user:
            request_user.set_password(new_password)
            request_user.save()
            return utils.api_json_response(200, 'Successfully password saved.')
        else:
            return utils.api_json_response(304, 'Unregistered user.')
    else:
        return utils.api_json_response(400, 'Invalid Request')