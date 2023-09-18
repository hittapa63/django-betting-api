from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import uuid
from django import template

register = template.Library()

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500, blank=True, null=True)
    fcm_token = models.CharField(max_length=300, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    firebase_uid = models.CharField(max_length=50, blank=True, null=True)
    provider_id = models.CharField(max_length=30, blank=True, null=True)
    social_type = models.CharField(max_length=30, blank=True, null=True) # google, facebook, apple, github, outlook, twitter
    birth_date = models.DateField(null=True, blank=True)
    photo = models.CharField(max_length=500, null=True, blank=True)
    chip = models.FloatField(default=200) # 1chip = $0.1
    exp = models.FloatField(default=0) # 25 exp for creating bet, 15 for placing a bet, 10 for every 10 people that joing your created bet, 0.5 for every 7 seconds spent scrolling on the app, 5 for betting 1 chip, 15 for betting 10 chips, 25 for betting 100 chips
    timezone = models.CharField(max_length=100, blank=True)
    bets = models.IntegerField(default=0) # count of creating bet
    winner_times = models.IntegerField(default=0)
    lose_times = models.IntegerField(default=0)
    tie_times = models.IntegerField(default=0)
    status = models.IntegerField(default=1) # 1: active, 0: deactive, 2: deleted user
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        self.user.is_active = True
        self.user.save()
        return str(self.user.id)

    def as_dict(self):
        return {
            'user_id': self.user.pk,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'address': self.address,
            'photo': self.photo,
            'exp': self.exp,
            'chip': self.chip,
            'timezone': self.timezone,
            'fcm_token': self.fcm_token,
            'winner_times': self.winner_times,
            'tie_times': self.tie_times,
            'lose_times': self.lose_times,
            'firebase_uid': self.firebase_uid,
            'provider_id': self.provider_id,
            'social_type': self.social_type,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

class SpotifyArtist(models.Model):
    # the reference result in here.

    # {
    #     'external_urls': {'spotify': 'https://open.spotify.com/artist/1YGAfUmqK5sYc1dIxNaOSn'}, 
    #     'followers': {'href': None, 'total': 345}, 
    #     'genres': [], 
    #     'href': 'https://api.spotify.com/v1/artists/1YGAfUmqK5sYc1dIxNaOSn', 
    #     'id': '1YGAfUmqK5sYc1dIxNaOSn', 
    #     'images': [
    #         {'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273a7388dd943a6a9dc62f9ec27', 'width': 640}, 
    #         {'height': 300, 'url': 'https://i.scdn.co/image/ab67616d00001e02a7388dd943a6a9dc62f9ec27', 'width': 300}, 
    #         {'height': 64, 'url': 'https://i.scdn.co/image/ab67616d00004851a7388dd943a6a9dc62f9ec27', 'width': 64}
    #         ], 
    #     'name': 'spotify', 
    #     'popularity': 0, 
    #     'type': 'artist', 
    #     'uri': 'spotify:artist:1YGAfUmqK5sYc1dIxNaOSn'
    # }
    external_urls = models.CharField(max_length=255, blank=True)
    followers = models.IntegerField(default=0)
    genres = models.CharField(max_length=999, blank=True) # the field is array value, so added comman to seperate the every value.
    artist_href = models.CharField(max_length=255, blank=True)
    image_height = models.IntegerField(default=0) # save the max size images
    image_width = models.IntegerField(default=0)
    image_url = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    artist_id = models.CharField(max_length=255, unique=True)
    popularity = models.FloatField(default=0)
    artist_uri = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.artist_id

    def as_dict(self):
        return {
            'id': self.pk,
            'external_urls': self.external_urls,
            'followers': self.followers,
            'genres': self.genres,
            'artist_href': self.artist_href,
            'image_url': self.image_url,
            'image_height': self.image_height,
            'image_width': self.image_width,
            'name': self.name,
            'artist_id': self.artist_id,
            'popularity': self.popularity,
            'artist_uri': self.artist_uri,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

class SpotifyArtistHistory(models.Model):
    artist = models.ForeignKey(SpotifyArtist, on_delete=models.CASCADE)
    followers = models.IntegerField(default=0)
    genres = models.CharField(max_length=999, blank=True) # the field is array value, so added comman to seperate the every value.
    popularity = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.artist.pk

    def as_dict(self):
        return {
            'id': self.pk,
            'external_urls': self.artist.external_urls,
            'followers': self.followers,
            'genres': self.genres,
            'artist_href': self.artist.artist_href,
            'image_url': self.artist.image_url,
            'image_height': self.artist.image_height,
            'image_width': self.artist.image_width,
            'name': self.artist.name,
            'artist_id': self.artist.artist_id,
            'popularity': self.popularity,
            'artist_uri': self.artist.artist_uri,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class AppleArtist(models.Model):
    # the reference result in here.

    # {
    #     'id': '1547088201', 
    #     'type': 'artists', 
    #     'href': '/v1/catalog/us/artists/1547088201', 
    #     'attributes': {
    #         'genreNames': [], 
    #         'name': 'Travis Laferrari Scott', 
    #         'url': 'https://music.apple.com/us/artist/travis-laferrari-scott/1547088201'
    #         }, 
    #     'relationships': {
    #         'albums': {
    #             'href': '/v1/catalog/us/artists/1547088201/albums', 
    #             'data': [
    #                 {
    #                     'id': '1547108190', 'type': 'albums', 'href': '/v1/catalog/us/albums/1547108190'
    #                 }
    #             ]
    #         }
    #     }
    # }
    external_urls = models.CharField(max_length=255, blank=True)
    followers = models.IntegerField(default=0)
    genres = models.CharField(max_length=999, blank=True) # the field is array value, so added comman to seperate the every value.
    artist_href = models.CharField(max_length=255, blank=True)
    image_height = models.IntegerField(default=0) # save the max size images
    image_width = models.IntegerField(default=0)
    image_url = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    artist_id = models.CharField(max_length=255, unique=True)
    play_counts= models.IntegerField(default=0)
    artist_uri = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.artist_id

class ArtistSearch(models.Model):
    music_type = models.CharField(max_length=30) # two type : 'spotify', 'apple'
    search_name = models.CharField(max_length=55)
    search_type = models.CharField(max_length=55) # artist, album etc.
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s" % self.search_name

class VerifyCode(models.Model):
    email = models.CharField(max_length=500)
    code = models.IntegerField()
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.email)

class Bet(models.Model):
    bet_uid = models.UUIDField(default=uuid.uuid4, editable=False)
    artist1 = models.ForeignKey(SpotifyArtist, on_delete=models.CASCADE, related_name='artist1')
    artist2 = models.ForeignKey(SpotifyArtist, on_delete=models.CASCADE, related_name='artist2')
    participants = models.CharField(max_length=2000, null=True, blank=True) # list of user id who take part in bet
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    is_opened = models.BooleanField(default=True)
    active_period = models.IntegerField(default=168) # period of bet active
    time_remained = models.IntegerField(default=72) # period of betting time period.
    initial_artist1_history = models.IntegerField()
    initial_artist2_history = models.IntegerField()
    last_artist1_history = models.IntegerField(default=0)
    last_artist2_history = models.IntegerField(default=0)
    winner_artist = models.IntegerField(default=0)
    bet_option = models.IntegerField(default=1) # 1: Who will be more popular this week? 2: Who will get more increase in streams this week?
    status = models.IntegerField(default=1) # 1: active, 2: deactive.
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.bet_uid)

    def as_dict(self):
        return {
            'id': self.pk,
            'bet_uid': self.bet_uid,
            'artist1_id': self.artist1.pk,
            'artist2_id': self.artist2.pk,
            'artist1_name': self.artist1.name,
            'artist2_name': self.artist2.name,
            'artist1_photo': self.artist1.image_url,
            'artist2_photo': self.artist2.image_url,
            'participants': self.participants,
            'bet_users': BetUser.objects.filter(bet=self).count(),
            'creator': self.creator.user.pk,
            'creator_photo': self.creator.photo,
            'creator_name': self.creator.user.username,
            'is_active': self.is_active,
            'is_opened': self.is_opened,
            'active_period': self.active_period,
            'time_remained': self.time_remained,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def bet_users_count(self):
        return BetUser.objects.filter(bet=self).count()

class BetUser(models.Model):
    bet = models.ForeignKey(Bet, on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    bet_artist = models.ForeignKey(SpotifyArtist, on_delete=models.CASCADE)
    bet_chip = models.FloatField()
    return_chip = models.FloatField(default=0.0) # return chips after betting result
    is_winner = models.BooleanField(null=True)
    is_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return {
            'id': self.pk,
            'user_id': self.user.user.pk,
            'email': self.user.user.email,
            'first_name': self.user.user.first_name,
            'last_name': self.user.user.last_name,
            'photo': self.user.photo,
            'bet_chip': self.bet_chip,
            'is_winner': self.is_winner,
            'is_end': self.is_end,
            'bet_artist': self.bet_artist.pk,
            'bet_artist_name': self.bet_artist.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Payment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cvv = models.CharField(max_length=50, blank=True, null=True)
    billing_address1 = models.CharField(max_length=500, blank=True, null=True)
    billing_address2 = models.CharField(max_length=500, blank=True, null=True)
    card_holder = models.CharField(max_length=500, blank=True, null=True)
    card_number = models.CharField(max_length=500)
    city = models.CharField(max_length=500, blank=True, null=True)
    exp_date = models.CharField(max_length=500, blank=True, null=True)
    payment_id = models.CharField(max_length=500)
    state = models.CharField(max_length=500, blank=True, null=True)
    zipcode = models.CharField(max_length=500, blank=True, null=True)
    amount = models.FloatField(default=0)
    payment_type = models.CharField(max_length=50, default='stripe')
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.payment_id)

    def get_real_amount(self):
        return round(self.amount/100, 2)

class ChipHistory(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    chip = models.FloatField() # purchased and won is plus, lost is minus.
    description = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return {
            'id': self.pk,
            'user_id': self.user.user.pk,
            'email': self.user.user.email,
            'username': self.user.user.username,
            'photo': self.user.photo,
            'chip': self.chip,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class UserInformation(models.Model):
    year = models.IntegerField(default=2021)
    month = models.IntegerField()
    month_users = models.IntegerField(default=0)
    month_active_users = models.IntegerField(default=0)
    month_deactive_users = models.IntegerField(default=0)
    total_users = models.IntegerField(default=0)
    total_active_users = models.IntegerField(default=0)
    total_deactive_users = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class BetInformation(models.Model):
    year = models.IntegerField(default=2021)
    month = models.IntegerField()
    month_bets = models.IntegerField(default=0)
    month_active_bets = models.IntegerField(default=0)
    month_deactive_bets = models.IntegerField(default=0)
    total_bets = models.IntegerField(default=0)
    total_active_bets = models.IntegerField(default=0)
    total_deactive_bets = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class BetChipInformation(models.Model):
    year = models.IntegerField(default=2021)
    month = models.IntegerField()
    month_wagers = models.FloatField(default=0) # chips used in betting
    month_returns = models.FloatField(default=0) # chips that give to winners
    month_profits = models.FloatField(default=0) # profit to us - admin
    total_wagers = models.FloatField(default=0)
    total_returns = models.FloatField(default=0)
    total_profits = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)