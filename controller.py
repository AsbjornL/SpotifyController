from player import get_device_id, access_token, get_queue_id, get_playlist_tracks, \
    remove_tracks_from_playlist, get_playback_state, set_playlist_id
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
    # Doesn't currently work, since player_loop doesn't respect the pause
    url = f"https://api.spotify.com/v1/me/player/pause?device_id={get_device_id()}"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.put(url, headers=headers)

    if response.status_code != 204:
        print(f"Pause failed: {response.reason}") 


def resume():
    url = f"https://api.spotify.com/v1/me/player/play?device_id={get_device_id()}"
    headers = {
        'Authorization': "Bearer " + access_token()
    }
    response = requests.put(url, headers=headers)

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


def remove_current_track():
    state = get_playback_state()
    if item := state.get('item'):
        cur_track = Track(item['name'], item['uri'])
        remove_tracks_from_playlist(get_queue_id(), [cur_track])


def queue_next(uri):
    url = f"https://api.spotify.com/v1/playlists/{get_queue_id()}/tracks"

    headers = {
        'Authorization': "Bearer " + access_token(),
        'Content-Type': 'application/json'
    }
    fields = {
        'uris': [uri],
        'position': 0
    }
    response = requests.post(url, headers=headers, json=fields)
    if response.status_code != 201:
        print("Queueing next track failed")
        raise Exception


def controller_loop():
    com = input("Enter command:\n> ")
    match com.split():
        case "skip", :
            print("skipping")
            remove_current_track()
            skip()

        case "print", "queue":
            queue = get_playlist_tracks(get_queue_id())
            print("Queue:")
            for i, track in enumerate(queue):
                print(f"\t{i+1}: {track.name},  uri: {track.uri}")

        case "exit", :
            print("closing down")
            return False
        
        case "remove", uri:
            print(f"Removing: {uri}")
            remove_tracks_from_playlist(get_queue_id(), [Track("placeholder", uri)])

        case "playlist", :
            set_playlist_id()

        case "queue", uri:
            print(f"Enqueueing {uri}")
            queue_next(uri)

        case _*:
            print("Unknown command")

    return True


if __name__ == '__main__':
    while controller_loop():
        pass

