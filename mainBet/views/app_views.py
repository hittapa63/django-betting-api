from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, QueryDict
from django.core import serializers
from django.forms.models import model_to_dict
from django.db.models import Q
from django.contrib.auth import authenticate, logout, login


from mainBet.utils import utils
from mainBet.models import Profile, Bet, SpotifyArtist

@csrf_exempt
def exp(request):
    if request.method == 'POST':
        try:
            exp = request.POST.get('exp', 0)
        except:
            exp = 0
        user_id = request.GET.get('uid')
        utils.add_exp_in_profile(user_id, exp)
        return utils.api_json_response(200, 'Successfully added Exp.')
    else:
        return utils.api_json_response(400, 'Invalid Request.')