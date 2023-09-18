from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import datetime
from django.contrib.auth import authenticate, logout, login


from mainBet.utils import utils
from mainBet.models import Profile, Bet, Payment, BetUser, ChipHistory

# get the 100 users based on the exp value.
# it is for the leaderboards in the app.
@csrf_exempt
def leader_boards(request):
    if request.method == 'GET':
        try:
            option = int(request.GET.get('option', 1))
        except:
            option = 1
        listset = []
        if option == 1:
            users = Profile.objects.order_by('-exp')[:100]
            listset = [x.as_dict() for x in users]
        if option == 2:
            start_date = datetime.datetime.now() - datetime.timedelta(days=7)
            end_date = datetime.datetime.now()
            bet_users = BetUser.objects.filter(is_end=True, created_at__range=(start_date, end_date))
            # if bet_users.count() == 0:
            users = Profile.objects.order_by('-winner_times')[:100]
            listset = [x.as_dict() for x in users]
        return utils.api_json_response(200, listset)
    else:
        return utils.api_json_response(400, 'Invalid Request.')

@csrf_exempt
def user(request, id):
    if request.method == 'GET':
        user = User.objects.filter(pk=id).first()
        if user == None:
            return utils.api_json_response(304, 'Not exist.')
        profile = Profile.objects.filter(user = user).first()
        if profile == None:
            return utils.api_json_response(304, 'Not exist.')
        user_info = model_to_dict(user, fields=['pk', 'email', 'username', 'first_name', 'last_name'])
        profile_info = model_to_dict(profile, fields=['user', 'address', 'fcm_token', 'winner_times', 'tie_times', 'lose_times', 'provider_id', 'social_type', 'photo', 'chip', 'exp', 'timezone', 'status'])
        info = user_info | profile_info
        return utils.api_json_response(200, [info])
    else:
        return utils.api_json_response(400, 'Invalid Request.')

# get users. 
# pagination is 100.
# get all users, get users by user_list 
@csrf_exempt
def users(request):
    if request.method == 'GET':
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        user_list = request.GET.get('user_list', None)
        if user_list != None:
            user_list = user_list.split(',')
            query_filter = {
                'user_id__in': user_list
            }
            users = Profile.objects.filter(**query_filter)
        else:
            users = Profile.objects.order_by('-created_at')[(page-1)*100: page*100]
        listset = [x.as_dict() for x in users]
        data = { 'page': page, 'total': users.count(), 'data': listset }
        return utils.api_json_response(200, data)
    else:
        return utils.api_json_response(400, 'Invalid Request.')

# stripe payment result information
# amount is invlaid (no number), return false.
@csrf_exempt
def payments(request):
    if request.method == 'POST':
        form_data = request.POST
        cvv = form_data.get('cvv', None)
        billing_address1 = form_data.get('billing_address1', None)
        billing_address2 = form_data.get('billing_address2', None)
        card_holder = form_data.get('card_holder', None)
        card_number = form_data.get('card_number', None)
        city = form_data.get('city', None)
        exp_date = form_data.get('exp_date', None)
        payment_id = form_data.get('payment_id', None)
        state = form_data.get('state', None)
        zipcode = form_data.get('zipcode', None)
        amount = form_data.get('amount', None)
        payment_type = form_data.get('payment_type', 'stripe')
        if card_number == None or payment_id == None or amount == None:
            return utils.api_json_response(304, 'Fields Required.')
        if card_number == '' or payment_id == '':
            return utils.api_json_response(304, 'Fields Required.')
        try:
            amount = float(amount)
        except:
            return utils.api_json_response(304, 'Amount Required.')
        user = User.objects.filter(pk=request.GET.get('uid')).first()
        profile = Profile.objects.filter(user = user).first()
        if profile == None:
            return utils.api_json_response(304, 'Not exist User.')
        profile.chip += amount/10
        profile.save()
        Payment.objects.create(
            user=profile,
            cvv=cvv,
            billing_address1 = billing_address1,
            billing_address2 = billing_address2,
            card_holder = card_holder,
            card_number = card_number,
            city = city,
            exp_date = exp_date,
            payment_id = payment_id,
            state = state,
            zipcode = zipcode,
            amount = amount,
            payment_type = payment_type
        )
        utils.record_chip_transaction(profile, amount/10, 'Purchased')
        return utils.api_json_response(200, 'Successfully Saved.')
    else:
        return utils.api_json_response(400, 'Invalid Request.')

# get the chip transactions ChipHistory
@csrf_exempt
def transactions(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id', request.GET.get('uid'))
        user = User.objects.filter(pk=user_id).first()
        if user == None:
            return utils.api_json_response(304, 'No exist user id')
        profile = Profile.objects.filter(user = user).first()
        if profile == None:
            return utils.api_json_response(304, 'Not exist user')
        histories = ChipHistory.objects.filter(user=profile).order_by('-created_at')
        listset = [x.as_dict() for x in histories]
        return utils.api_json_response(200, listset)
    else:
        return utils.api_json_response(400, 'Invalid Request.')
