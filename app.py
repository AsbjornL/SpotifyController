from flask import Flask, redirect
from autherize import auth_url

app = Flask(__name__)

@app.route('/autherize')
def auth():
    return redirect(auth_url(), code=302)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

