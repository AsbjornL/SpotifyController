from player import get_device_id, access_token
from structs import Track
import requests

def skip():
    url = f"https://api.spotify.com/v1/me/player/next?device_id={get_device_id()}"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.post(url, headers=headers)

    if response.status_code != 204:
        print("Skip failed")


def pause():
    url = f"https://api.spotify.com/v1/me/player/pause?device_id={get_device_id()}"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.post(url, headers=headers)

    if response.status_code != 204:
        print("Pause failed") 


def resume():
    url = f"https://api.spotify.com/v1/me/player/play?device_id={get_device_id()}"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.post(url, headers=headers)

    if response.status_code != 204:
        print("Resume failed") 


def get_current_track_queue():
    url = "https://api.spotify.com/v1/me/player/queue"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Get current track and queue failed")
        raise Exception

    res_json = response.json()
    cur = None
    if currently_playing := res_json['currently_playing']:
        cur = Track(currently_playing['name'], currently_playing['uri'])

    queue = []
    for tune in res_json['queue']:
        if Track(tune['name'], None) in queue:
            continue
        queue.append(Track(tune['name'], tune['uri']))

    return cur, queue


def controller_loop():
    com = input("Enter command:\n> ")
    match com:
        case "skip":
            skip()
        case "print queue":
            cur, queue = get_current_track_queue()
            print (f"Currently Playing:\n\t0: {cur.name},  uri:{cur.uri}")
            print("Queue:")
            for i, track in enumerate(queue):
                print(f"\t{i+1}: {track.name},  uri:{track.uri}")
        case "exit":
            return False
        case "pause":
            pause()

    return True


if __name__ == '__main__':
    while controller_loop():
        pass
