from flask import Flask, redirect, request, render_template, url_for
from waitress import serve
from autherize import auth_url
from player import access_token, set_device_id, load_backup, set_playlist_id, create_queue, start_playback, toggle_shuffle, player_loop
import requests


app = Flask(__name__)
BACKUP = "webapp_backup.txt"


def clear_backup():
    open(BACKUP, 'w').close()


@app.route("/")
def start():
    return redirect(url_for('authorize'))


@app.route("/autherize")
def auth():
    return redirect(auth_url(url_for('start_playback')), code=302)


@app.route("/start_playback", methods=['GET', 'POST'])
def choose_device():
    token = access_token()

    url = "https://api.spotify.com/v1/me/player/devices"
    headers = {
        'Authorization': "Bearer " + token
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "Getting devices failed", 500

    devices = response.json()['devices']

    if not devices:
        return "No available devices", 404

    if request.method == 'POST':
        if 'clear_cache' in request.form:
            clear_backup()
        load_backup(BACKUP)
        create_queue()
        set_playlist_id()

        device_id = request.form['device_id']
        set_device_id(device_id)

        start_playback()
        toggle_shuffle()
        player_loop()
        return f"Device {device_id} selected successfully!"

    return render_template('choose_device.html', devices=devices)


if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)

