#  this is the future working using Firebase
#  need to regist web in the Firebase newly.

# import pyrebase
import firebase_admin
from firebase_admin import credentials, auth

# config = {
#     "apiKey": "AIzaSyDm3yqIkxMS0iZwWquwJZI6DeMZkNnlSGg",
#     "authDomain": "okbet-310817.firebaseapp.com",
#     "databaseURL": "https://okbet-310817-default-rtdb.firebaseio.com/",
#     "projectId": "okbet-310817",
#     "storageBucket": "okbet-310817.appspot.com",
#     "messagingSenderId": "1090770966217",
#     "appId": "1:1090770966217:web:5f796e6e07928efc2adf18",
#     "measurementId": "G-4SSEW2ZL0F"
# }

# firebase = pyrebase.initialize_app(config)
# auth = firebase.auth()
# database = firebase.database()

cred = credentials.Certificate('config/okbet-firebase.json')
firebase_admin.initialize_app(cred)

def get_user_info_with_token(id_token):
    try:
        print(id_token)
        uidExist = auth.verify_id_token(id_token)
        print(uidExist)
        return uidExist
    except:
        return None

def get_user_info_with_uid(uid):
    try:
        print(uid)
        uidExist = auth.get_user(uid)
        return uidExist
    except:
        return None