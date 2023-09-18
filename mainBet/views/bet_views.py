from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core import serializers
from django.forms.models import model_to_dict
from django.db.models import Q
from django.contrib.auth import authenticate, logout, login

from mainBet.utils import utils, admin_utils
from mainBet.models import Profile, Bet, SpotifyArtist, SpotifyArtistHistory, BetUser

#  get the artists from spotify table.
# pagination is 100.
@csrf_exempt
def artists(request):
    if request.method == 'GET':
        search_name = request.GET.get('search_name', None)
        try:
            page = int(request.GET.get('page', 1))
        except:
            page = 1
        if search_name == None:
            artists = SpotifyArtist.objects.all()[(page-1)*100: page*100]
        else:
            artists = SpotifyArtist.objects.filter(name__contains = search_name)[(page-1)*100: page*100]
        listset = [x.as_dict() for x in artists]
        data = {'page': page, 'total': artists.count(), 'search_name': search_name, 'data': listset}
        return utils.api_json_response(200, data)
    else:
        return utils.api_json_response(400, 'Invalid Request.')

# get the artist from spotify by id(pk).
@csrf_exempt
def artist(request, id):
    if request.method == 'GET':
        artist = SpotifyArtist.objects.get(id=id)
        artist_info = model_to_dict(artist)
        return utils.api_json_response(200, [artist_info])
    else:
        return utils.api_json_response(400, 'Invalid Request.')

# create bet and get bets lists.
# required fields: artists id and name, and created user id.
@csrf_exempt
def bets(request):
    if request.method == 'POST':
        data = request.POST
        artist1_id = data.get('artist1', None)
        artist2_id = data.get('artist2', None)
        try:
            bet_option = int(data.get('bet_option', 1))
        except:
            bet_option = 1
        if (artist1_id == None or artist2_id == None):
            return utils.api_json_response(304, 'Fields Required.')
        if (artist1_id == artist2_id):
            return utils.api_json_response(304, 'Only one artist selected. Please select another for bet.')
        artist1 = SpotifyArtist.objects.get(id=artist1_id)
        artist2 = SpotifyArtist.objects.get(id=artist2_id)
        if artist1 == None or artist2 == None:
            return utils.api_json_response(304, 'The artist is not existed in our service.')
        user = User.objects.get(id=request.GET.get('uid'))
        profile = Profile.objects.filter(user = user).first()
        artist1_history = SpotifyArtistHistory.objects.filter(artist=artist1).order_by('-created_at').first()
        artist2_history = SpotifyArtistHistory.objects.filter(artist=artist2).order_by('-created_at').first()
        bet = Bet.objects.create(
            creator=profile,
            artist1=artist1,
            artist2=artist2,
            bet_option = bet_option,
            initial_artist1_history = artist1_history.pk,
            initial_artist2_history = artist2_history.pk,
        )
        bet.save()
        profile.bets += 1
        profile.save()
        utils.add_exp_in_profile(user.pk, 25)
        bet_info = bet.as_dict()
        data = { 'bet' : bet_info, 'bet_users': get_betusers(bet) }
        admin_utils.record_bet_information(bet, is_new=True)
        return utils.api_json_response(200, [data])
    if request.method == 'GET':
        data = request.GET
        try:
            page = int(data.get('page', 1))
        except:
            page = 1
        is_active = data.get('is_active', None)
        user_id = data.get('user_id', None)
        search_name = data.get('search_name', None)
        query_filters = {}
        if (is_active):
            query_filters['is_active'] = is_active
        if user_id:
            user = User.objects.filter(pk=user_id).first()
            profile = Profile.objects.filter(user = user).first()
            if user == None:
                return utils.api_json_response(304, 'There is not user in our service.')
            query_filters['creator'] = profile
        if search_name == None:
            bets = Bet.objects.filter(**query_filters).order_by('-created_at')[(page-1)*100: page*100]
        else:
            # bets = Bet.objects.filter(**query_filters).order_by('-created_at')[(page-1)*100: page*100]
            bets = Bet.objects.filter(**query_filters).filter(Q(artist1__name__contains=search_name) | Q(artist2__name__contains=search_name))[(page-1)*100: page*100]
        listset = [{'bet': x.as_dict(), 'bet_users': get_betusers(x)} for x in bets]
        data_info = { 'page': page, 'search_name': search_name, 'total': bets.count(), 'user_id': user_id, 'data': listset }
        return utils.api_json_response(200, data_info)
    else:
        return utils.api_json_response(400, 'Invalid Request')

@csrf_exempt
def bet(request, id):
    # just need to join in the bet.
    if request.method == 'PATCH':
        data = QueryDict(request.body)
        if not 'user_id' in data:
            return utils.api_json_response(304, 'Required Fields.')
        user = User.objects.filter(pk=data['user_id']).first()
        bet_chip = 0
        bet_artist = 0
        try:
            bet_chip = int(data['bet_chip'])
            bet_artist = int(data['bet_artist'])
        except:
            return utils.api_json_response(304, 'Required Correct Fields.')
        bet = Bet.objects.filter(pk=id).first()
        if user == None or bet == None:
            return utils.api_json_response(304, 'No exist bet or request user information in our service.')
        # if str(bet.creator.pk) == data['user_id']:
        #     return utils.api_json_response(304, 'This user is create of this bet.')
        if bet.is_opened == False or bet.is_opened == False:
            return utils.api_json_response(304, 'The active time of betting is expired. Please put another betting.')
        if bet.status == 0:
            return utils.api_json_response(304, 'This bet is deactive state.')
        if bet_artist != bet.artist1_id and bet_artist != bet.artist2_id:
            return utils.api_json_response(304, 'The bet artist is not exist in bet.')
        participants = []
        profile = Profile.objects.filter(user = user).first()
        if profile.chip - bet_chip < 0:
            return utils.api_json_response(304, 'Your chip is small to place in bet.')
        if bet.participants != None:
            participants = bet.participants.split(',')
        if str(user.pk) in participants:
            return utils.api_json_response(304, 'You already put in this bet.')
            # BetUser.objects.filter(bet=bet, user=profile).update(bet_chip=bet_chip)
            # utils.add_chip_in_profile(user.pk, -bet_chip)
            # bet_info = model_to_dict(bet)
            # data = { 'bet' : [bet_info], 'bet_users': get_betusers(bet) }
            # return utils.api_json_response(200, data)
        else:
            participants.append(data['user_id'])
            bet.participants = ','.join(participants)
            bet.save()
            if len(participants) % 10 == 0:
                utils.add_exp_in_profile(bet.creator.pk, 10)
            BetUser.objects.create(
                user=profile,
                bet=bet,
                bet_artist=SpotifyArtist.objects.filter(pk=bet_artist).first(),
                bet_chip=bet_chip,
            )
            utils.add_exp_in_profile(user.pk, 15)
            utils.add_chip_in_profile(user.pk, -bet_chip)
            utils.record_chip_transaction(profile, -bet_chip, 'Put on Bet.')
            admin_utils.record_bet_chip_information(bet_chip, 0, 0)
            # bet_info = model_to_dict(bet)
            bet_info = bet.as_dict()
            utils.send_push_notification([bet.creator], 'New Better', 'New user is joined in your bet.')
            data = { 'bet' : bet_info, 'bet_users': get_betusers(bet) }
            return utils.api_json_response(200, [data])

    if request.method == 'GET':
        bet = Bet.objects.filter(pk=id).first()
        if bet == None:
            return utils.api_json_response(304, 'No exists bet.')
        # bet_info = model_to_dict(bet)
        bet_info = bet.as_dict()
        data = { 'bet' : bet_info, 'bet_users': get_betusers(bet) }
        return utils.api_json_response(200, [data])
    else:
        return utils.api_json_response(400, 'Invalid Request')

def get_betusers(bet):
    bet_users = BetUser.objects.filter(bet=bet)
    listset = [x.as_dict() for x in bet_users]
    return listset

def bet_win(request, id):
    bet = Bet.objects.filter(pk=id).first()
    if bet == None:
        return utils.api_json_response(304, 'No existed Bet')
    if bet.is_active == False:
        return utils.api_json_response(304, 'The bet was already expired.')
    if bet.status == 0:
        return utils.api_json_response(304, 'This bet is deactive state.')
    bet.is_active = False
    bet.is_opened = False
    bet.active_period = 0
    bet.time_remained = 0
    bet.save()
    utils.confirm_bet(bet)
    admin_utils.record_bet_information(bet, is_new=False)
    return utils.api_json_response(200, 'checked')


