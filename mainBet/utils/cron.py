from mainBet.models import VerifyCode, Bet, ArtistSearch
from mainBet.utils import utils, admin_utils
from mainBet.views import third_views

def scheduled_betting():
    print("----- cron1 working -----")
    verify_code = VerifyCode.objects.create(
        email='ftfaaa@gmail.com',
        code=000000
    )
    verify_code.save()
    bets = Bet.objects.filter(is_active=True)
    for bet in bets:
        bet.active_period -=1
        bet.time_remained -=1
        if bet.time_remained < 0:
            bet.time_remained = 0
        if bet.active_period == 0:
            bet.is_active = False
        if bet.time_remained == 0:
            bet.is_opened = False
        bet.save()
        if bet.is_active == False:
            utils.confirm_bet(bet)
            admin_utils.record_bet_information(bet, is_new = False)

def scheduled_get_artists():
    print("----- cron2 working -----")
    artist_searches = ArtistSearch.objects.filter(is_active=True)
    for artist_search in  artist_searches:
        if artist_search.music_type == 'apple':
            third_views.get_artists_from_apple(artist_search.search_type, artist_search.search_name)
        else:
            third_views.get_artists_from_spotify(artist_search.search_type, artist_search.search_name)
