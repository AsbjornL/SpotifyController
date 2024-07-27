from flask import Flask, redirect
from autherize import auth_url
from player import run_player


app = Flask(__name__)


@app.route('/autherize')
def auth():
    return redirect(auth_url(), code=302)


@app.route('/player')
def play():
    run_player()
    return "Playing done"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

