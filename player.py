from structs import Track
from time import sleep
from datetime import date
from enum import IntEnum
from random import shuffle
import conf
import requests


queue_id = ""
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


def get_playlist_tracks(playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    url += "?fields=next,items(track(name,uri))"
    url += "&limit=50"
    url += "&offset=0"
    headers = {
        'Authorization': "Bearer " + access_token()
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


def set_playlist_id():
    id = input("Enter playlist id:\n> ")

    if get_playlist_tracks(id):
        url = conf.url + "/set_playlist"
        fields = {
            'id': id
        }
        response = requests.post(url, data=fields)
        if (response.status_code != 200):
            print("Setting playlist id failed")

    else:
        print("Playlist didn't have any tracks. Trying again")
        set_playlist_id()


def set_device_id(device_id):
    url = conf.url + "/device_id"
    fields = {
        'id': device_id
    }
    response = requests.post(url, data=fields)
    if (response.status_code != 200):
        print("Settings device id failed")


def choose_device_id():
    url = "https://api.spotify.com/v1/me/player/devices"
    headers = {
        'Authorization': "Bearer " + access_token()
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


def get_user_id():
    url = "https://api.spotify.com/v1/me"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Getting user id failed")
        raise Exception
    return response.json()['id']


def create_queue():
    name = "API queue " + str(date.today())
    url = f"https://api.spotify.com/v1/users/{get_user_id()}/playlists"
    headers = {
        'Authorization': "Bearer " + access_token(),
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
    
    global queue_id
    queue_id = response.json()['id']


def add_tracks_to_queue(tracks):
    for track in tracks:
        track_status[track] = max(track_status.get(track, Status.NEW), Status.QUEUED)

    url = f"https://api.spotify.com/v1/playlists/{queue_id}/tracks"

    headers = {
        'Authorization': "Bearer " + access_token(),
        'Content-Type': 'application/json'
    }
    fields = {
        'uris': [t.uri for t in tracks],
    }
    response = requests.post(url, headers=headers, json=fields)
    if response.status_code != 201:
        print("Adding tracks to queue failed")
        raise Exception


def remove_tracks_from_playlist(playlist_id, tracks):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

    headers = {
        'Authorization': "Bearer " + access_token(),
        'Content-Type': 'application/json'
    }
    fields = {
        'tracks': [{'uri': t.uri} for t in tracks]
    }
    response = requests.delete(url, headers=headers, json=fields)
    if response.status_code != 200:
        print("Removing tracks from playlist failed")
        raise Exception


def get_playback_state():
    url = "https://api.spotify.com/v1/me/player"
    headers = {
        'Authorization': "Bearer " + access_token(),
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed getting playback state")
        raise Exception
    return response.json()


def start_playback():
    url = f"https://api.spotify.com/v1/me/player/play?device_id={get_device_id()}"
    headers = {
        'Authorization': "Bearer " + access_token(),
        'Content-Type': "application/json"
    }
    fields = {
        'context_uri': "spotify:playlist:" + queue_id,
    }

    response = requests.put(url, headers=headers, json=fields)

    if response.status_code != 204:
        print("Starting playback failed")


def player_loop():
    global track_status
    while True:
        queue = get_playlist_tracks(queue_id)

        state = get_playback_state()
        if item := state.get('item'):
            cur_track = Track(item['name'], item['uri'])
            track_status[cur_track] = max(track_status.get(cur_track, Status.NEW), Status.PLAYED)

        played = [track for track in queue if track_status.get(track, Status.QUEUED) >= Status.PLAYED and track.name != conf.default_track_name]
        if played:
            remove_tracks_from_playlist(queue_id, played)

        if len(queue) < conf.queue_size:
            print(f"Queue length is {len(queue)}. Adding track")
            candidates = get_playlist_tracks(get_playlist_id())
            shuffle(candidates)
            for track in candidates:
                if track_status.get(track, Status.NEW) >= Status.QUEUED:
                    continue
                next_track = track
                break
            else:
                print(f"No more songs in playlist. Adding {conf.default_track_name}")
                next_track = Track(conf.default_track_name, conf.default_track_uri)

            add_tracks_to_queue([next_track])

        if not state['is_playing']:
            start_playback()

        elif state['device']['id'] != get_device_id():
            set_device_id(state['device']['id'])

        sleep(5)


if __name__ == '__main__':
    create_queue()
    set_playlist_id() 
    choose_device_id()
    start_playback()
    player_loop()

