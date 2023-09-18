# Betting API and Admin Panel

## technical stack
- [spotipy api](https://spotipy.readthedocs.io/en/2.18.0/#client-credentials-flow)
- [cron tab](https://pypi.org/project/django-crontab/)
- [push notification with firebase](https://fcm-django.readthedocs.io/en/latest/)

## installation
```bash
export SPOTIPY_CLIENT_ID='<Your Spotify client id>'
export SPOTIPY_CLIENT_SECRET='<Your Spotify client secret>'
mkvirtualenv venv -p python3
pip install -r requirements.txt
python3.9 manage.py crontab show
python3.9 manage.py crontab remove
python3.9 manage.py crontab add
python3.9 manage.py runserver
```