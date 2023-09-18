from django.urls import path
from django.conf.urls import url
from mainBet.views import third_views

urlpatterns = [
    path('spotify/search', third_views.spotify_search),
    path('apple/search', third_views.apple_search),
]