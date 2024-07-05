from structs import Track
from time import sleep
from datetime import date
from enum import IntEnum
from random import shuffle
import conf
import requests


track_status = {}


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

    pid = input("Enter playlist id:\n> ")

    if get_playlist_tracks(pid, token=token):
        url = conf.url + "/set_playlist"
        fields = {
            'id': pid
        }
        response = requests.post(url, data=fields)
        if (response.status_code != 200):
            print("Setting playlist id failed")

    else:
        print("Playlist didn't have any tracks. Trying again")
        set_playlist_id(token=token)


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


def player_loop():
    global track_status
    while True:
        info = get_token_and_ids()
        queue_id = info['qid']
        device_id = info['did']
        playlist_id = info['pid']
        token = info['token']
        queue = get_playlist_tracks(queue_id, token=token)

        state = get_playback_state(token=token)
        if item := state.get('item'):
            cur_track = Track(item['name'], item['uri'])
            track_status[cur_track] = max(track_status.get(cur_track, Status.NEW), Status.PLAYED)

        played = [track for track in queue if track_status.get(track, Status.QUEUED) >= Status.PLAYED and track.name != conf.default_track_name]
        if played:
            remove_tracks_from_playlist(queue_id, played, token=token)

        for track in queue:
            # Just in case
            track_status[track] = max(track_status.get(track, Status.QUEUED), Status.QUEUED)

        if len(queue) < conf.queue_size:
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

            add_tracks_to_queue([next_track], qid=queue_id, token=token)

        if not state['is_playing']:
            start_playback(qid=queue_id, did=device_id, token=token)

        elif state['device']['id'] != device_id:
            set_device_id(state['device']['id'])

        sleep(5)


if __name__ == '__main__':
    print("Creating Queue")
    create_queue()
    print("Setting playlist id")
    set_playlist_id() 
    print("Choosing device")
    choose_device_id()
    print("Starting playback")
    start_playback()
    print("Starting player loop")
    player_loop()

