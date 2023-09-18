from django.http import HttpResponse, JsonResponse
import datetime
from django.contrib.auth.models import User
from mainBet.models import UserInformation, BetInformation, BetChipInformation

# json response for the admin
def admin_json_response(status, data, message):
    if (status == 200):
        status_value = True
    else:
        status_value = False
    return JsonResponse({'status': status_value, 'data': data, 'message': message}, status=status)

def record_user_information(profile, is_new = False):
    year = datetime.datetime.today().year
    month = datetime.datetime.today().month
    total_users = 0
    total_active_users = 0
    total_deactive_users = 0
    user_information = UserInformation.objects.filter(year= year, month= month).first()
    last_user_information = UserInformation.objects.last()
    if last_user_information != None:
        total_users = last_user_information.total_users
        total_active_users = last_user_information.total_active_users
        total_deactive_users = last_user_information.total_deactive_users
    
    if user_information == None:
        user_information = UserInformation.objects.create(
            year= year,
            month = month,
            total_users = total_users,
            total_active_users = total_active_users,
            total_deactive_users = total_deactive_users
        )
        user_information.save()
    if is_new == True:
        user_information.month_users += 1
        user_information.month_active_users += 1
        user_information.total_active_users += 1
        user_information.total_users += 1
    else:
        if profile.status == 1:
            user_information.month_active_users += 1
            user_information.month_deactive_users -= 1
            user_information.total_active_users += 1
            user_information.total_deactive_users -= 1
        else:
            user_information.month_active_users -= 1
            user_information.month_deactive_users += 1
            user_information.total_active_users -= 1
            user_information.total_deactive_users += 1

    user_information.updated_at = datetime.datetime.now()
    user_information.save()

def record_bet_information(bet, is_new = False):
    year = datetime.datetime.today().year
    month = datetime.datetime.today().month
    total_bets = 0
    total_active_bets = 0
    total_deactive_bets = 0
    bet_information = BetInformation.objects.filter(year= year, month= month).first()
    last_bet_information = BetInformation.objects.last()
    if last_bet_information != None:
        total_bets = last_bet_information.total_bets
        total_active_bets = last_bet_information.total_active_bets
        total_deactive_bets = last_bet_information.total_deactive_bets
    
    if bet_information == None:
        bet_information = BetInformation.objects.create(
            year= year,
            month = month,
            total_bets = total_bets,
            total_active_bets = total_active_bets,
            total_deactive_bets = total_deactive_bets
        )
        bet_information.save()
    if is_new == True:
        bet_information.month_bets += 1
        bet_information.month_active_bets += 1
        bet_information.total_active_bets += 1
        bet_information.total_bets += 1
    else:
        if bet.status == 1 and bet.is_active == True:
            bet_information.month_active_bets += 1
            bet_information.month_deactive_bets -= 1
            bet_information.total_active_bets += 1
            bet_information.total_deactive_bets -= 1
        else:
            bet_information.month_active_bets -= 1
            bet_information.month_deactive_bets += 1
            bet_information.total_active_bets -= 1
            bet_information.total_deactive_bets += 1
    bet_information.updated_at = datetime.datetime.now()
    bet_information.save()

def record_bet_chip_information(wager, return_chip, profits):
    year = datetime.datetime.today().year
    month = datetime.datetime.today().month
    month_wager = wager
    month_return_chip = return_chip
    month_profits = profits
    total_wager = wager
    total_return_chip = return_chip
    total_profits = profits
    bet_chip_information = BetChipInformation.objects.filter(year= year, month= month).first()
    last_bet_chip_information = BetChipInformation.objects.last()
    if last_bet_chip_information != None:
        total_wager += last_bet_chip_information.total_wagers
        total_return_chip += last_bet_chip_information.total_returns
        total_profits += last_bet_chip_information.total_profits
    if bet_chip_information == None:
        bet_chip_information = BetChipInformation.objects.create(
            year=year,
            month = month,
            month_wagers= month_wager,
            month_returns= month_return_chip,
            month_profits= month_profits,
            total_wagers= total_wager,
            total_returns= total_return_chip,
            total_profits= total_profits
        )
        bet_chip_information.save()
    else:
        bet_chip_information.month_wagers += month_wager
        bet_chip_information.month_returns += month_return_chip
        bet_chip_information.month_profits += month_profits
        bet_chip_information.total_wagers += month_wager
        bet_chip_information.total_returns += month_return_chip
        bet_chip_information.total_profits += month_profits
        bet_chip_information.updated_at = datetime.datetime.now()
        bet_chip_information.save()

