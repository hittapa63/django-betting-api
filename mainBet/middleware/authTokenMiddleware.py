from mainBet.utils import utils
from mainBet.models import Profile

class BaseMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

class authTokenMiddleware(BaseMiddleware):
    def process_view(self, request, view_func, view_args, view_kwargs):
        TOKEN_TYPE = "Bearer "
        API_PRE_URL = '/api'
        ALLOWED_URL_LISTS = [
            "/api/register",
            "/api/login",
            "/api/request-forgot-password",
            "/api/verify-code",
            "/api/set-password",
            "/api/social/login",
        ]
        
        path = request.path
        if API_PRE_URL in path and path not in ALLOWED_URL_LISTS:
            token = request.headers.get('Authorization')
            if token == None  or TOKEN_TYPE not in token:
                return utils.api_json_response(304, 'Invalid Request. Login Required')
            token = token.replace(TOKEN_TYPE, '')
            if utils.verify_token(token, request):
                return None
            else:
                return utils.api_json_response(304, 'Invalide Token.')
        return None