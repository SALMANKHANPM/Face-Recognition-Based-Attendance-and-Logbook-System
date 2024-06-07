import os

import cv2
from flask import Flask, render_template, Response, request, send_from_directory, redirect, url_for, session, flash
from model import model, detectFace
from firebaseHandler import initializeFirebase, displayMembers, insertReason, addUser
import requests
from werkzeug.utils import secure_filename
import secrets

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)

UPLOAD_FOLDER = 'Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

bucket, db, auth = initializeFirebase()
app.secret_key = secret_key

try:
    bucket, db, auth = initializeFirebase()
except Exception as e:
    print(f"Error initializing Firebase: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logging')
def logging():
    if 'user' not in session:
        return redirect(url_for('signin'))

    return render_template('logging.html')


@app.route('/video_feed/<int:mode>', methods=['GET', 'POST'])
def video_feed(mode):
    return Response(genFrames(mode), mimetype='multipart/x-mixed-replace; boundary=frame')


def genFrames(mode):
    while True:
        frame_gen = model(db, mode)
        for frame in frame_gen:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/takeAttendance', methods=["GET", "POST"])
def takeAttendance():
    if 'user' not in session:
        return redirect(url_for('signin'))
    mode = 0
    return render_template("takeattendance.html", mode=mode)


@app.route('/logbook', methods=['GET', 'POST'])
def logbook():
    return 'WIP, SEE YOU SOON!'


@app.route('/logging/login', methods=['GET', 'POST'])
def logbookLogin():
    if 'user' not in session:
        return redirect(url_for('signin'))
    mode = 1
    return render_template('logbooklogin.html', mode=mode)


@app.route('/logging/reason', methods=['GET', 'POST'])
def logbookReason():
    if 'user' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        reasonData = request.form['reason']
        insertReason(reasonData)

        return redirect(url_for('logbookLogin', mode=1))

    return render_template('logbookreason.html')


@app.route('/logging/logout')
def logbookLogout():

    if 'user' not in session:
        return redirect(url_for('signin'))

    mode = 2
    return render_template('logbooklogout.html', mode=mode)


@app.route('/attendancelogbook', methods=["GET", "POST"])
def attendance():
    if 'user' not in session:
        return redirect(url_for('signin'))

    if request.method == "POST":
        model(db)

    students = displayMembers()
    return render_template("logbook.html", data=students, tableSize=len(students))


@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for('signin'))

    return render_template("dashboard.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session["user"] = email
            user = auth.refresh(user['refreshToken'])
            return redirect(url_for("dashboard"))
        except requests.exceptions.HTTPError as e:
            response = 'Invalid Credentials'
            return render_template("signin.html", response=response)

    return render_template("signin.html")


@app.route("/signout")
def signout():
    session.pop("user", None)
    return redirect(url_for("/"))


@app.route('/preline.js')
def serve_preline_js():
    return send_from_directory('node_modules/preline/dist', 'preline.js')


# WIP

@app.route('/studentRegistration', methods=["GET", "POST"])
def studentRegistration():
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if 'user' not in session:
        return redirect(url_for('signin'))

    if request.method == "POST":
        name = request.form["name"]
        studentID = request.form["studentID"]
        email = request.form["email"]
        branch = request.form["branch"]

        print(name, studentID, email, branch)

        # Check if the post request has the file part
        if 'file-input' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file-input']
        print(file.filename)

        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(studentID + '.' + file.filename.rsplit('.', 1)[1].lower())
            print('After Rename: ', filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Create directory if not exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            file.save(file_path)

            try :
                bucket.child(f"Images/{filename}").put(file_path)
            except Exception as e:
                print(f"Error uploading image: {e}")

            session['registeredData'] = studentID
            # Add user to Firebase
            addUser(studentID, name, branch, email)
            return redirect(url_for('dashboard'))

    return render_template("studentRegistration.html")


# @app.route('/studentRegistration', methods=["GET", "POST"])
# def studentRegistration():
#     if 'user' not in session:
#         return redirect(url_for('signin'))
#
#     if request.method == "POST":
#         name = request.form["name"]
#         studentID = request.form["studentID"]
#         email = request.form["email"]
#         branch = request.form["branch"]
#
#         session['registeredData'] = studentID
#         # Add user to Firebase
#         addUser(studentID, name, branch, email)
#         return redirect(url_for('studentRegistration/capture'))
#
#     return render_template("studentRegistration.html")
#
#
# @app.route('/studentRegistration/capture', methods=["GET", "POST"])
# def captureImage():
#     if request.method == "POST":
#         frame = detectFace()
#         imgFileName = f"{session['registeredData']['id']}.jpg"
#         cv2.imwrite(f'images/{imgFileName}', frame)
#
#         addUser(session['registeredData']['id'], session['registeredData']['name'], session['registeredData']['branch'],
#                 session['registeredData']['email'])
#         bucket.child(f"images/{imgFileName}").put(f'images/{imgFileName}')
#
#     return render_template("captureImage.html")


# if __name__ == "__main__":
#     app.config['DEBUG'] = False
#     app.run(debug=True, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
