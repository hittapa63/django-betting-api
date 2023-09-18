from django.http import HttpResponse, JsonResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import applemusicpy
import os
from django.views.decorators.csrf import csrf_exempt
import datetime
from mainBet.models import SpotifyArtist, AppleArtist, SpotifyArtistHistory, ArtistSearch
from mainBet.utils import utils

auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

# must code just like underlined for teh secret_key
secret_key = """-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg0s8iY/Gzgp5ZIqI8
qUGV0amfTDq6P46gRJfVjNJQnn2gCgYIKoZIzj0DAQehRANCAAQhCmDjlZNYfNdL
WWUurmSMqIEvix7/D49PaWAzEidVPBUeYXw8Cq+0KRB6hddxLQdRLi224UCjC+t5
6tzCQPSA
-----END PRIVATE KEY-----"""
key_id = os.environ.get('APPLE_MUSIC_KEY_ID')
team_id = os.environ.get('APPLE_TEAM_ID')

am = applemusicpy.AppleMusic(secret_key, key_id, team_id)

# Create your views here.

# get the artist information from spotify using search name field.
@csrf_exempt
def spotify_search(request):
    if request.method != 'GET':
        return utils.api_json_response(400, 'Invalid Request')
    search_field = request.GET.get('q', 'spotify')
    search_type = request.GET.get('type', 'artist')
    artist_search = ArtistSearch.objects.filter(search_name=search_field, search_type=search_type, music_type='spotify').first()
    if artist_search == None:
        ArtistSearch.objects.create(
            music_type='spotify',
            search_name=search_field,
            search_type=search_type
        )
    get_artists_from_spotify(search_type, search_field)
    return utils.api_json_response(200, 'ok')

# get the artists from apple just like spotify way.
# may need to remove this, cause could not get the total counts of performance.
# also, could not get the photo of artist.
@csrf_exempt
def apple_search(request):
    if request.method == 'POST':
        return utils.api_json_response(400, 'Invalid Request')
    search_field = request.GET.get('q', 'scott')
    search_type = request.GET.get('type', 'artists')
    artist_search = ArtistSearch.objects.filter(search_name=search_field, search_type=search_type, music_type='apple').first()
    if artist_search == None:
        ArtistSearch.objects.create(
            music_type='apple',
            search_name=search_field,
            search_type=search_type
        )
    get_artists_from_apple(search_type, search_field, search_field)
    return utils.api_json_response(200, 'ok')

def get_artists_from_spotify(search_type, search_field):
    result = sp.search(q='artist: ' + search_field, type=search_type, limit=50)
    items = result['artists']['items']
    print('----- this is the artists length ----- ' + str(len(items)))
    if len(items) >0:
        for i, item in enumerate(items):
            if item['popularity'] >= 60:
                spotify_artist = SpotifyArtist.objects.filter(artist_id=item['id']).first()
                if spotify_artist:
                    spotify_artist.external_urls = item['external_urls']['spotify']
                    spotify_artist.followers = item['followers']['total']
                    spotify_artist.genres = ",".join(item['genres'])
                    spotify_artist.artist_href = item['href']
                    if len(item['images']) > 0:
                        spotify_artist.image_height = item['images'][0]['height']
                        spotify_artist.image_width = item['images'][0]['width']
                        spotify_artist.image_url = item['images'][0]['url']
                    spotify_artist.name = item['name']
                    spotify_artist.popularity = item['popularity']
                    spotify_artist.artist_uri = item['uri']
                    spotify_artist.updated_at = datetime.datetime.now()
                    spotify_artist.save()
                else:
                    spotify_artist = SpotifyArtist()
                    spotify_artist.external_urls = item['external_urls']['spotify']
                    spotify_artist.followers = item['followers']['total']
                    spotify_artist.genres = ",".join(item['genres'])
                    spotify_artist.artist_href = item['href']
                    if len(item['images']) > 0:
                        spotify_artist.image_height = item['images'][0]['height']
                        spotify_artist.image_width = item['images'][0]['width']
                        spotify_artist.image_url = item['images'][0]['url']
                    spotify_artist.name = item['name']
                    spotify_artist.artist_id = item['id']
                    spotify_artist.popularity = item['popularity']
                    spotify_artist.artist_uri = item['uri']
                    spotify_artist.save()
                spotify_artist_history = SpotifyArtistHistory.objects.create(
                    artist=spotify_artist,
                    followers=spotify_artist.followers,
                    genres=spotify_artist.genres,
                    popularity=spotify_artist.popularity
                )

def get_artists_from_apple(search_type, search_field):
    results = am.search(search_field, types=[search_type], limit=10)
    items = results['results']['artists']['data']
    if len(items) >0:
        for i, item in enumerate(items):
            # if item['popularity'] >= 60:
                apple_artist = AppleArtist.objects.filter(artist_id=item['id']).first()
                if apple_artist:
                    apple_artist.genres = ",".join(item['attributes']['genreNames'])
                    apple_artist.artist_href = item['attributes']['url']
                    apple_artist.name = item['attributes']['name']
                    apple_artist.play_counts = int(item['id'])
                    apple_artist.artist_uri = item['attributes']['url']
                    apple_artist.save()
                else:
                    apple_artist = AppleArtist()
                    apple_artist.genres = ",".join(item['attributes']['genreNames'])
                    apple_artist.artist_href = item['attributes']['url']
                    apple_artist.name = item['attributes']['name']
                    apple_artist.play_counts = int(item['id'])
                    apple_artist.artist_uri = item['attributes']['url']
                    apple_artist.artist_id = item['id']
                    apple_artist.save()
