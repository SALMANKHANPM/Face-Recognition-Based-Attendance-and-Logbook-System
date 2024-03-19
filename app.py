from flask import Flask, render_template, Response, request, send_from_directory, flash, redirect, url_for
from model import model
from firebaseHandler import initializeFirebase


app = Flask(__name__)
bucket, db, auth = initializeFirebase()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cameraFeed')
def CameraFeed():
    # Render the HTML template for the video feed
    return render_template('videofeed.html')


@app.route('/video_feed')
def video_feed():
    data = model(db)
    return Response(data, mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/attendance')
def attendance():
    return "Attendance Page"


@app.route('/studentRegistration')
def studentRegistration():
    return "Student Registration Page"

@app.route("/dashboard")
def dashboard():
    return 'Dashboard'

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            return redirect(url_for("dashboard"))
        except Exception as e:
            if 'INVALID_PASSWORD' in str(e):
                response = 'Invalid Password'
            elif 'EMAIL_NOT_FOUND' in str(e):
                response = 'Email not found'
            elif 'USER_DISABLED' in str(e):
                response = 'User is disabled'
            else:
                response = str(e)
            return render_template("signin.html", response=response)
    return render_template("signin.html")


@app.route('/preline.js')
def serve_preline_js():
    return send_from_directory('node_modules/preline/dist', 'preline.js')


if __name__ == "__main__":
    app.config['DEBUG'] = False
    app.secret_key = "b'\x98\x85\xf6\xb5\x06\xbb\x01\xfb\x7f\xa7\x04{\x1937\x17\xd3\x87\xdbQ\xfa[\xd2v'"
    app.run(debug=True, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))
