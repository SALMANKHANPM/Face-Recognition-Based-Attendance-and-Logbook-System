# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
# from firebase_admin import storage
# from firebase_admin import auth
#
# def initializeFirebase():
#     try:
#         cred = credentials.Certificate('ServiceAccountKey.json')
#         firebase_admin.initialize_app(cred, {
#             "authDomain": "klglugattendence.firebaseapp.com",
#             "databaseURL": "https://klglugattendence-default-rtdb.firebaseio.com",
#             "storageBucket": "klglugattendence.appspot.com",
#
#         })
#
#         print("Firebase Initialized")
#         authentication = firebase_admin.auth
#         bucket = storage.bucket()
#         database = db.reference("Students")
#         return bucket, database, authentication
#     except ConnectionError as e:
#         print("Connection Error: ", e)
#         pass
#

import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyD2XVmgvS5PanrZWROWLJ3418UinBnEVLI",
    "authDomain": "klglugattendence.firebaseapp.com",
    "databaseURL": "https://klglugattendence-default-rtdb.firebaseio.com",
    "projectId": "klglugattendence",
    "storageBucket": "klglugattendence.appspot.com",
    "messagingSenderId": "139657088619",
    "appId": "1:139657088619:web:23d8aa1415cf682f32ab2e"
}


def initializeFirebase():
    try:
        firebase = pyrebase.initialize_app(firebaseConfig)
        authentication = firebase.auth()
        database = firebase.database()
        storageBucket = firebase.storage()
        return storageBucket, database, authentication
    except ConnectionError as e:
        print("Connection Error: ", e)
