from django.http import HttpResponse, JsonResponse
from jose import jws, jwt
import datetime
from validate_email import validate_email
import random
from pyfcm import FCMNotification
from django.contrib.auth.models import User, Group

from mainBet.models import Profile, SpotifyArtistHistory, BetUser, SpotifyArtist, ChipHistory
from mainBet.utils import admin_utils

push_service = FCMNotification(api_key="AAAA_fcEFsk:APA91bHfG5J8JGkDzOOVGE6tCq4_2sQ7WXuw2abnBYrtFZRrCDdARcmfEjG3SBJHy-_pg6y0iygEJ93ZFb4PWbIOBsZ3Z4ShrorZZeZK-YPBYWDsnG9aGk2jmrul0_76-u4FVSLyHMa7")


def get_domain(request):
    return request.build_absolute_uri('/')[:-1]
# json response for the api
def api_json_response(status, data):
    if (status == 200):
        status_value = True
    else:
        status_value = False
    return JsonResponse({'status': status_value, 'data': data}, status=200)

# generate the token using python-jose
# need to check the python-jose
# input value user id and expire days from current day
# return value token
def generate_token(id, day):
    expiry = datetime.date.today() + datetime.timedelta(days=day)
    token = jwt.encode({ 'id': id, 'expiry' : expiry.strftime("%Y-%m-%d %H:%M:%S") }, 'secret',  algorithm='HS256')
    return token

def verify_token(token, request):
    try:
        profile = Profile.objects.filter(token=token)
        if not profile.exists():
            return False
        data = jwt.decode(token, 'secret', algorithms=['HS256'])
        expiry = datetime.datetime.strptime(data['expiry'], "%Y-%m-%d %H:%M:%S")
        if (expiry < datetime.datetime.today()):
            return False
        uid = data['id']
        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET['uid'] = uid
        return True
    except:
        return False

def json_response(status, message):
    st = True
    if status == 0:
        st = False
    data = {
        'status': st,
        'data': message
    }
    return data

# register post data validation part.
# username, password first_name last_name email confirm_password address provider_id social_type birth_date
def register_validation(form_data):
    username = form_data.get('username', -1)
    password = form_data.get('password', -1)
    first_name = form_data.get('first_name', -1)
    last_name = form_data.get('last_name', -1)
    email = form_data.get('email', -1)
    confirm_password = form_data.get('confirm_password', -1)
    address = form_data.get('address', -1)
    provider_id = form_data.get('provider_id', -1)
    social_type = form_data.get('social_type', -1)
    birth_date = form_data.get('birth_date', -1)
    if username == -1:
        return json_response(0, 'username is required')
    if password == -1:
        return json_response(0, 'password is required')
    if email == -1:
        return json_response(0, 'email is required')
    # if first_name == -1:
    #     return json_response(0, 'FirstName is required')
    # if last_name == -1:
    #     return json_response(0, 'LastName is required')
    if confirm_password == -1:
        return json_response(0, 'confirm_password is required')
    if validate_email(email) == False:
        return json_response(0, 'Invalid email')
        # is_valid = validate_email('example@example.com',verify=True)
        # Returns True if the email exist in real world else False.
    user = User.objects.filter(username=username)
    if user.exists():
        return json_response(0, 'This username is already existed.')
    user = User.objects.filter(email=email)
    if user.exists():
        return json_response(0, 'This email is already existed.')
    if password != confirm_password:
        return json_response(0, 'Password does not match.')
    return json_response(1, 'Validated')

def add_exp_in_profile(user_id, exp):
    user = User.objects.filter(pk=user_id).first()
    profile = Profile.objects.filter(user = user).first()
    profile.exp += float(exp)
    profile.save()

def add_chip_in_profile(user_id, chip):
    user = User.objects.filter(pk=user_id).first()
    profile = Profile.objects.filter(user = user).first()
    profile.chip += float(chip)
    profile.save()

# determine the betting win.
# check the spotify artist history that are get by cronjob  every day.
# compare the porpularity.
# if same the popularity, compare the followers.
# if tie a bet, need to refund the chips to users.
def confirm_bet(bet):
    profile_lists = []

    # get 2 artists information from database
    initial_artist1_history = SpotifyArtistHistory.objects.filter(pk=int(bet.initial_artist1_history)).first()
    initial_artist2_history = SpotifyArtistHistory.objects.filter(pk=int(bet.initial_artist2_history)).first()
    last_artist1_history = SpotifyArtistHistory.objects.filter(artist=initial_artist1_history.artist).order_by('-created_at').first()
    last_artist2_history = SpotifyArtistHistory.objects.filter(artist=initial_artist2_history.artist).order_by('-created_at').first()
    bet.last_artist1_history = last_artist1_history.pk
    bet.last_artist2_history = last_artist2_history.pk

    # determine the winner artist just some logic
    is_tie = True
    winner_artist_id = 0
    if bet.bet_option == 1:
        artist1_delta_popularity = last_artist1_history.popularity - initial_artist1_history.popularity
        artist2_delta_popularity = last_artist2_history.popularity - initial_artist2_history.popularity
        if artist2_delta_popularity != artist1_delta_popularity:
            is_tie = False
            if artist1_delta_popularity > artist2_delta_popularity:
                winner_artist_id = bet.artist1.pk
            else:
                winner_artist_id = bet.artist2.pk
    else:
        artist1_delta_stream = last_artist1_history.followers - initial_artist1_history.followers
        artist2_delta_stream = last_artist2_history.followers - initial_artist2_history.followers
        if artist1_delta_stream != artist1_delta_stream:
            is_tie = False
            if artist1_delta_stream > artist2_delta_stream:
                winner_artist_id = bet.artist1.pk
            else:
                winner_artist_id = bet.artist2.pk
    
    if is_tie:
        # just need to determine the betting, cause the popularity does not change in real time.
        # so confirm the betting between 2 artists by random competition.
        random_value = random.randint(0, 4)
        if random_value != 0:
            is_tie = False
            if random_value % 2 == 0:
                winner_artist_id = bet.artist2.pk
            else:
                winner_artist_id = bet.artist1.pk
    
    # winner, loser update in bet user table.
    if is_tie == False:
        bet_artist = SpotifyArtist.objects.filter(pk=winner_artist_id).first()
        BetUser.objects.filter(bet=bet, bet_artist=bet_artist).update(is_winner=True)
        BetUser.objects.filter(bet=bet, is_winner=None).update(is_winner=False)
        bet.winner_artist = winner_artist_id
    bet.save()
    # give the chip to the winners.
    wagers_pools_returns(bet)


# For each bet, there are three wager tiers: 1 okchip, 10 okchips, and 100 okchips (you can only bet either 1, 10, or 100)
# Add up the wager entries for each tier
# If 5 people bet 1 chip, 6 people bet 10 chips, and 7 people bet 100 chips then you’d have 3 pools
# Pool #1 is 5 chips, pool #2 is 60 chips, pool #3 is 700 chips
# The pools cannot be combined because the returns would be less than the wager for some players even if they won
# OkBet takes a 10% fee from each pool.
# The returns are the chips the winners get back after they win. The return is the pool divided by the number of winners in a pool. If you lose, you get no returns.
# If you bet 1 chip in pool #1 and with 5 participants, then the pool is 5 chips
# OkBet takes 10% of the pool, so the pool becomes 4.5 chips
# If you and two other players win, then the pool of 4.5 chips is divided by 3 and distributed to each winner. So each winner gets 1.5 chips in return
# The same is done for the other price tiers
# Returns = (pool - 10%) / (number of winners)
def wagers_pools_returns(bet):
    pool_list = []
    bet_users = BetUser.objects.filter(bet=bet)
    total_return_chips = 0
    total_wagers = 0
    for bet_user in bet_users:
        bet_user.is_end = True
        profile = Profile.objects.filter(pk=bet_user.user.pk).first()
        total_wagers += bet_user.bet_chip
        if bet.winner_artist == 0:
            profile.chip += bet_user.bet_chip
            bet_user.return_chip = bet_user.bet_chip
            profile.tie_times += 1
            profile.save()
            total_return_chips += bet_user.bet_chip
            record_chip_transaction(profile, bet_user.bet_chip, 'Bet Tied')
        else:
            is_calculated = False
            for pool in pool_list:
                if pool['chip'] == bet_user.bet_chip:
                    is_calculated = True
                    pool['betters'] += 1
                    if bet_user.is_winner == True:
                        pool['winners'].append(bet_user.user)
            if is_calculated == False:
                if bet_user.is_winner == True:
                    data = { 'chip': bet_user.bet_chip, 'betters': 1, 'winners': [bet_user.user] }
                else:
                    data = { 'chip': bet_user.bet_chip, 'betters': 1, 'winners': [] }
                pool_list.append(data)
            if bet_user.is_winner == True:
                profile.winner_times += 1
            else:
                profile.lose_times += 1
            profile.save()
        bet_user.save()
    for pool in pool_list:
        for bet_user_winner in pool['winners']:
            profile = Profile.objects.filter(pk=bet_user_winner.pk).first()
            return_chip = round(pool['chip'] * pool['betters'] * 0.9 / len(pool['winners']), 2)
            BetUser.objects.filter(bet=bet, user=profile).update(return_chip=return_chip)
            profile.chip += return_chip
            profile.save()
            total_return_chips += return_chip
            record_chip_transaction(profile, return_chip, 'Bet Win')
    admin_utils.record_bet_chip_information(0, total_return_chips, total_wagers-total_return_chips)

def send_push_notification(profiles, title, body):
    fcm_lists = []
    for profile in profiles:
        if profile.fcm_token != None:
            fcm_lists.append(profile.fcm_token)
    if len(fcm_lists) > 0:
        result = push_service.notify_multiple_devices(registration_ids=fcm_lists, message_title=title, message_body=body, sound='Default')
        print(result)

def record_chip_transaction(profile, chip, description):
    chip_history = ChipHistory.objects.create(
        user= profile,
        chip=chip,
        description = description
    )
    chip_history.save()