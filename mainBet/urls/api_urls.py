from django.urls import path
from django.conf.urls import url
from mainBet.views import auth_views, bet_views, user_views, app_views

urlpatterns = [
    # auth part
    path('register', auth_views.register),
    path('login', auth_views.sign_in),
    path('change-password', auth_views.change_password),
    path('request-forgot-password', auth_views.request_forgot_password),
    path('verify-code', auth_views.verify_code),
    path('set-password', auth_views.set_password), # forgot password part
    path('update', auth_views.update), # update profile
    path('social/login', auth_views.social_login),

    # main part
    path('artists', bet_views.artists),
    path('artists/<int:id>', bet_views.artist),
    path('bets', bet_views.bets),
    path('bets/<int:id>', bet_views.bet),
    path('bets/win/<int:id>', bet_views.bet_win),
    path('leaderboards', user_views.leader_boards),
    path('users', user_views.users),
    path('users/<int:id>', user_views.user),
    path('exp', app_views.exp),
    path('payments', user_views.payments),
    path('chip-transactions', user_views.transactions),
]