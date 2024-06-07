from app import app

if __name__ == "__main__":
    app.config['DEBUG'] = False
    app.run(debug=True, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))