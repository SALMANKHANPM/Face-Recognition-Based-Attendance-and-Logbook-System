from flask import Flask, render_template, Response, request, send_from_directory, flash, redirect, url_for, session, g
from model import model
from firebaseHandler import initializeFirebase
import requests


import secrets

secret_key = secrets.token_urlsafe(16)

app = Flask(__name__)
bucket, db, auth = initializeFirebase()
app.secret_key = secret_key

try:
    bucket, db, auth = initializeFirebase()
except Exception as e:
    print(f"Error initializing Firebase: {e}")


# Rest of your code...

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cameraFeed')
def CameraFeed():
    if 'user' not in session:
        return redirect(url_for('signin'))

    with app.app_context():
        model(db)
    # Render the HTML template for the video feed
    return render_template('takeattendance.html', response=g.studentInfo)


@app.route('/video_feed')
def video_feed():
    return Response(genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def genFrames():
    while True:
        frame_gen = model(db)
        for frame in frame_gen:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/takeAttendance', methods=["GET", "POST"])
def takeAttendance():
    try:
        # if 'user' not in session:
        #     return redirect(url_for('signin'))

        if request.method == "POST":
            model(db)

        with app.app_context():
            studentData = model(db)

        if studentData is None:
            return render_template("takeattendance.html", studentData=None)

    except StopIteration as e:
        studentData = None
    return render_template("takeattendance.html", studentData=studentData)


@app.route('/attendance')
def attendance():
    if 'user' not in session:
        return redirect(url_for('signin'))

    return "Attendance Page"


@app.route('/studentRegistration')
def studentRegistration():
    if 'user' not in session:
        return redirect(url_for('signin'))

    return "Student Registration Page"


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
            if e.response is not None:
                response = e.response.json()
                print(response)
                return render_template("signin.html", response=response)

    return render_template("signin.html")


@app.route("/signout")
def signout():
    session.pop("user", None)
    return redirect(url_for("signin"))


@app.route('/preline.js')
def serve_preline_js():
    return send_from_directory('node_modules/preline/dist', 'preline.js')


if __name__ == "__main__":
    app.config['DEBUG'] = False
    # app.secret_key = "b'\x98\x85\xf6\xb5\x06\xbb\x01\xfb\x7f\xa7\x04{\x1937\x17\xd3\x87\xdbQ\xfa[\xd2v'"
    app.run(debug=True, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
