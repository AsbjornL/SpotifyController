from structs import Track
from time import sleep
from datetime import date
from enum import IntEnum
from random import shuffle
import conf
import requests
import json


track_status = {}
backup = ""


class Status(IntEnum):
    NEW = 0
    QUEUED = 1
    PLAYED = 2


def access_token():
    url = conf.url + "/token"
    response = requests.get(url)
    token = response.json()['token']
    return token


def get_playlist_id():
    url = conf.url + "/playlist_id"
    response = requests.get(url)
    return response.json()['id']


def get_device_id():
    url = conf.url + "/device_id"
    response = requests.get(url)
    return response.json()['id']


def get_queue_id():
    url = conf.url + "/queue_id"
    response = requests.get(url)
    return response.json()['id']


def get_token_and_ids():
    url = conf.url + "/info"
    response = requests.get(url)
    return response.json()


def get_playlist_tracks(playlist_id, token=None):
    token = token or access_token()

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    url += "?fields=next,items(track(name,uri))"
    url += "&limit=50"
    url += "&offset=0"
    headers = {
        'Authorization': "Bearer " + token
    }

    tracks = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Gettings tracks failed")
            return tracks

        res_json = response.json()
        for tune in res_json['items']:
            tracks.append(Track(tune['track']['name'], tune['track']['uri']))

        url = res_json['next']

    return tracks


def set_playlist_id(token=None):
    token = token or access_token()

    pid = conf.default_playlist_id

    if get_playlist_tracks(pid, token=token):
        url = conf.url + "/set_playlist"
        fields = {
            'id': pid
        }
        response = requests.post(url, data=fields)
        if (response.status_code != 200):
            print("Setting playlist id failed")

    else:
        print("Default playlist didn't have any tracks")
        raise Exception


def set_device_id(device_id):
    url = conf.url + "/device_id"
    fields = {
        'id': device_id
    }
    response = requests.post(url, data=fields)
    if (response.status_code != 200):
        print("Setting device id failed")


def set_queue_id(queue_id):
    url = conf.url + "/queue_id"
    fields = {
        'id': queue_id
    }
    response = requests.post(url, data=fields)
    if (response.status_code != 200):
        print("Setting queue id failed")


def choose_device_id(token=None):
    token = token or access_token()

    url = "https://api.spotify.com/v1/me/player/devices"
    headers = {
        'Authorization': "Bearer " + token
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Gettings devices failed")
        raise Exception

    devices = response.json()['devices']

    if not devices:
        print("No available devices")
        raise Exception

    print("Available devices:")
    for i, d in enumerate(devices):
        print(f"\t{i}. {d['name']}")

    pick = int(input("Choose a device number\n> "))

    device_id = devices[pick]['id']
    set_device_id(device_id)


def get_user_id(token=None):
    token = token or access_token()

    url = "https://api.spotify.com/v1/me"
    headers = {
        'Authorization': "Bearer " + token
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Getting user id failed")
        raise Exception
    return response.json()['id']


def create_queue(token=None):
    token = token or access_token()

    if qid := get_queue_id():
        ans = input("Queue playlist already exists. Reuse? (y/n)\n>")
        if ans in {"y", "Y"}:
            return

    name = "API queue " + str(date.today())
    url = f"https://api.spotify.com/v1/users/{get_user_id(token=token)}/playlists"
    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/json'
    }
    fields = {
        'name': name,
        'public': False
    }
    response = requests.post(url, headers=headers, json=fields)

    if response.status_code != 201:
        print("Creating queue playlist failed: ", response.reason)
        raise Exception
   
    set_queue_id(response.json()['id'])


def add_tracks_to_queue(tracks, qid=None, token=None):
    qid = qid or get_queue_id()
    token = token or access_token()

    for track in tracks:
        track_status[track] = max(track_status.get(track, Status.NEW), Status.QUEUED)

    url = f"https://api.spotify.com/v1/playlists/{qid}/tracks"

    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/json'
    }
    fields = {
        'uris': [t.uri for t in tracks],
    }
    response = requests.post(url, headers=headers, json=fields)
    if response.status_code != 201:
        print("Adding tracks to queue failed")
        raise Exception


def remove_tracks_from_playlist(playlist_id, tracks, token=None):
    token = token or access_token()

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': 'application/json'
    }
    fields = {
        'tracks': [{'uri': t.uri} for t in tracks]
    }
    response = requests.delete(url, headers=headers, json=fields)
    if response.status_code != 200:
        print(f"Removing tracks from playlist failed: {response.text}")
        raise Exception


def get_playback_state(token=None):
    token = token or access_token()

    url = "https://api.spotify.com/v1/me/player"
    headers = {
        'Authorization': "Bearer " + token,
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()

    if response.status_code == 204:
        return {'is_playing' : False}

    print("Failed getting playback state")
    raise Exception

def start_playback(qid=None, did=None, token=None):
    url = conf.url + "/start_player"
    response = requests.put(url)
    if response.status_code != 200:
        print("Asking main server to start player failed")

    qid = qid or get_queue_id()
    did = did or get_device_id()
    token = token or access_token()

    url = f"https://api.spotify.com/v1/me/player/play?device_id={did}"
    headers = {
        'Authorization': "Bearer " + token,
        'Content-Type': "application/json"
    }
    fields = {
        'context_uri': "spotify:playlist:" + qid,
    }

    response = requests.put(url, headers=headers, json=fields)

    if response.status_code != 204:
        print("Starting playback failed")


def toggle_shuffle(token=None, did=None):
    token = token or access_token()
    did = did or get_device_id()

    url = f"https://api.spotify.com/v1/me/player/shuffle?state=false&device_id={did}"

    headers = {
        'Authorization': "Bearer " + token
    }

    response = requests.put(url, headers=headers)
    if response.status_code not in {200, 204}:
        print(f"Toggle shuffle failed, {response.reason}")


def choose_backup():
    choice = input("Write name of storage file\n> ")
    load_backup(choice)


def load_backup(file_name):
    global backup
    backup = file_name
    try:
        tracks = []
        with open(file_name, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    tracks.append(Track(**data))
                except Exception as e:
                    print(f"Loading line \"{line}\", failed: {e}")
        global track_status
        track_status = {t: Status.PLAYED for t in tracks}
        print(f"{len(track_status)} played tracks loaded from backup")
    except FileNotFoundError:
        print("Creating new storage file")
        open(backup, 'w')


def write_to_backup(track):
    with open(backup, 'a') as f:
        json.dump(track.to_dict(), f)
        f.write("\n")


def is_paused():
    url = conf.url + "/paused"

    response = requests.get(url)
    if response.status_code != 200:
        print("Get paused status failed")
        return False

    return response.json()['paused']


def player_loop():
    global track_status
    while True:
        print("Loopin'")
        if is_paused():
            sleep(conf.player_loop_time)
            continue

        info = get_token_and_ids()
        queue_id = info['qid']
        device_id = info['did']
        playlist_id = info['pid']
        token = info['token']
        queue = get_playlist_tracks(queue_id, token=token)
        if info['stop']:
            print("Player stopping")
            break

        state = get_playback_state(token=token)
        if item := state.get('item'):
            cur_track = Track(item['name'], item['uri'])
            if track_status.get(cur_track, Status.NEW) < Status.PLAYED:
                track_status[cur_track] = Status.PLAYED
                write_to_backup(cur_track)

        played = [track for track in queue if track_status.get(track, Status.QUEUED) >= Status.PLAYED and track.name != conf.default_track_name]
        if played:
            remove_tracks_from_playlist(queue_id, played, token=token)

        for track in queue:
            # Just in case
            track_status[track] = max(track_status.get(track, Status.QUEUED), Status.QUEUED)

        has_default = any(t.name == conf.default_track_name for t in queue)

        if len(queue) < conf.queue_size or has_default:
            print(f"Queue length is {len(queue)}. Adding track")
            candidates = get_playlist_tracks(playlist_id, token=token)
            shuffle(candidates)
            for track in candidates:
                if track_status.get(track, Status.NEW) >= Status.QUEUED:
                    continue
                next_track = track
                break
            else:
                print(f"No more songs in playlist. Adding {conf.default_track_name}")
                next_track = Track(conf.default_track_name, conf.default_track_uri)

            if len(queue) < conf.queue_size or next_track.name != conf.default_track_name:
                add_tracks_to_queue([next_track], qid=queue_id, token=token)

            if next_track.name != conf.default_track_name and has_default:
                # A new song. Clear out all defaults
                remove_tracks_from_playlist(queue_id, [Track(conf.default_track_name, conf.default_track_uri)], token=token)

        if not state['is_playing']:
            start_playback(qid=queue_id, did=device_id, token=token)

        elif state['device']['id'] != device_id:
            set_device_id(state['device']['id'])

        sleep(conf.player_loop_time)


if __name__ == '__main__':
    choose_backup()
    print("Creating Queue")
    create_queue()
    print("Setting playlist id")
    set_playlist_id() 
    print("Choosing device")
    choose_device_id()
    print("Starting playback")
    start_playback()
    print("Toggling shuffle off")
    toggle_shuffle()
    print("Starting player loop")
    player_loop()

