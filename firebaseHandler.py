import pyrebase
import datetime as dt

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


userDB = initializeFirebase()[1]


def addUser(stuID, name, branch, email):
    data = {
        stuID: {
            'name': name,
            'studentID': stuID,
            'email': email,
            'branch': branch,
            'login_log': [None],
            'total_login': 0,
            'created_at': dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_login': None,
            'logout': False
        }
    }
    for key, value in data.items():
        userDB.child('Students').child(key).set(value)
    print(f"User {id} added to database")


def login(sid, login):
    user_ref = userDB.child('Students').child(sid)
    user = user_ref.get().val()

    if user:
        # Ensure 'login_Log' exists and is a list, or initialize it as an empty list
        login_log = user.get('login_Log', []) if isinstance(user.get('login_Log'), list) else []

        # Append the new login time
        login_log.append(login)

        # Update total login count
        total_login = user.get('total_login') + 1

        # Update user data
        user_data = {
            'last_Login': login,
            'Login_Log': login_log,
            'total_Login': total_login +  1,
            'logout': True
        }

        userDB.child('Students').child(sid).update(
            {'last_Login': login, 'total_login': total_login, 'login_Log': login_log})
        # Update user in the database
        # user_ref.update(user_data)
        print(f"User {sid} updated in the database")


def logout(sid):
    user_ref = userDB.child('Students').child(sid)
    user = user_ref.get().val()

    if user:
        user_data = {
            'logout': False
        }

        # Update user in the database
        user_ref.child('Students').child(sid).update(user_data)

        print(f"User {sid} logged out in the database")
