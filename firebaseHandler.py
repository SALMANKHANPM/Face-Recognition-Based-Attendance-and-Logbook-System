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


# Attendance Schema for Firebase

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
            'total_Login': total_login + 1,
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


def displayMembers():
    users = userDB.child('Students').get().val()
    return users.values()


# LOGBOOK
def logbookScehma(sid=None, reason=None, login=None):
    logbook = {
        dt.date.today().strftime("%Y-%m-%d"): {
            sid: {
                'reasons': [reason],
                'loginTimes': [login],
                'logoutTimes': [],
                'loggedIn': True  # If Logged in, True else False
            }
        }
    }

    for key, value in logbook.items():
        userDB.child('Logbook').child(key).set(value)
    print(f"Logbook entry added to database")


# logbookScehma('2200080183', 'Login 1', dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def logbookLogin(sid, reason):
    login_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logbook_entry = userDB.child('Logbook').child(dt.date.today().strftime("%Y-%m-%d")).child(sid).get().val()

    if logbook_entry:
        # Check if user is already logged in
        if logbook_entry.get('loggedIn', False):  # Default to False if key does not exist
            return f"User {sid} is already logged in; new login is not recorded."
        else:
            # Check if 'loginTimes' key exists, if not initialize it
            if 'loginTimes' not in logbook_entry:
                logbook_entry['loginTimes'] = []
            if 'reasons' not in logbook_entry:
                logbook_entry['reasons'] = []

            # Append the login time and reason
            logbook_entry['loginTimes'].append(login_time)
            logbook_entry['reasons'].append(reason)
            logbook_entry['loggedIn'] = True

            # Update the entry in the database
            userDB.child('Logbook').child(dt.date.today().strftime("%Y-%m-%d")).child(sid).update(logbook_entry)
            return f"User {sid} logged in at {login_time} for reason: {reason}."
    else:
        # If logbook_entry does not exist, create a new entry with the login and reason
        logbook_entry = {
            'reasons': [reason],
            'loginTimes': [login_time],
            'logoutTimes': [],
            'loggedIn': True
        }
        userDB.child('Logbook').child(dt.date.today().strftime("%Y-%m-%d")).child(sid).set(logbook_entry)
        return f"Logbook entry created and user {sid} logged in at {login_time} for reason: {reason}."



def logbookLogout(sid) -> str:
    logout_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logbook_entry = userDB.child('Logbook').child(dt.date.today().strftime("%Y-%m-%d")).child(sid).get().val()

    if logbook_entry:
        # Check if user is already logged in
        if logbook_entry.get('loggedIn', False):  # Default to False if key does not exist
            # If 'logoutTimes' key doesn't exist, initialize it
            if 'logoutTimes' not in logbook_entry:
                logbook_entry['logoutTimes'] = []

            # Append the logout time
            logbook_entry['logoutTimes'].append(logout_time)
            logbook_entry['loggedIn'] = False

            # Update the entry in the database
            userDB.child('Logbook').child(dt.date.today().strftime("%Y-%m-%d")).child(sid).update(logbook_entry)
            return f"{sid} logged out at {logout_time}."
        else:
            return f"{sid} is not logged in; logout not required."
    else:
        return f"No logbook entry found"


def insertReason(reason) -> None:
    data = {
        'msg': reason
    }
    userDB.child('Reasons').update(data)
    print('Reason added to database')


def fetchAndDeleteReason():
    reason = userDB.child('Reasons').get().val()
    print(reason['msg'])
    userDB.child('Reasons').remove()
    return reason['msg']
