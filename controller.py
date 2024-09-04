from player import get_device_id, access_token, get_queue_id, get_playlist_tracks, \
	remove_tracks_from_playlist, get_playback_state
from structs import Track
import requests
import conf


prev_queue = {}


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


def skip():
	url = f"https://api.spotify.com/v1/me/player/next?device_id={get_device_id()}"
	headers = {
		'Authorization': "Bearer " + access_token()
	}
	response = requests.post(url, headers=headers)

	if response.status_code not in (200, 204):
		print(f"Skip failed: {response.reason}")


def pause():
	# Doesn't currently work, since player_loop doesn't respect the pause
	url = f"https://api.spotify.com/v1/me/player/pause?device_id={get_device_id()}"
	headers = {
		'Authorization': "Bearer " + access_token()
	}
	response = requests.put(url, headers=headers)

	if response.status_code not in {200, 204}:
		print(f"Pause failed on Spotify: {response.reason}") 

	url = conf.url + "/pause"
	response = requests.put(url)

	if response.status_code != 200:
		print("Pause failed on local")


def resume():
	url = f"https://api.spotify.com/v1/me/player/play?device_id={get_device_id()}"
	headers = {
		'Authorization': "Bearer " + access_token()
	}
	response = requests.put(url, headers=headers)

	if response.status_code not in {200, 204}:
		print("Resume failed on Spotify") 

	url = conf.url + "/resume"
	response = requests.put(url)

	if response.status_code != 200:
		print("Resume failed on local")



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


def actual_queue(uri):
	url = f"https://api.spotify.com/v1/me/player/queue?device_id={get_device_id()}"
	url += f"&uri={uri}"
	headers = {
		'Authorization': "Bearer " + access_token(),
		'Content-Type': 'application/json'
	}

	response = requests.post(url, headers=headers)
	if response.status_code not in {200, 204}:
		print("Adding to actual queue failed")


def stop_player():
	url = conf.url + "/stop_player"
	response = requests.put(url)

	if response.status_code != 200:
		print("Asking server to stop player failed")


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
				prev_queue[i+1] = track
				print(f"\t{i+1}: {track.name},	uri: {track.uri}")

		case "exit", :
			print("closing down")
			return False

		case "stop", "player":
			print("Stopping player")
			stop_player()

		case "remove", choice:
			if choice.isdigit():
				if track := prev_queue.get(int(choice)):
					uri = track.uri
				else:
					print("No track matching number given")
					return True
			else:
				uri = choice
			print(f"Removing: {uri}")
			remove_tracks_from_playlist(get_queue_id(), [Track("placeholder", uri)])

		case "playlist", :
			set_playlist_id()

		case "queue", uri:
			print(f"Enqueueing {uri}")
			queue_next(uri)

		case "force", "queue", uri:
			print(f"Force enqueueing {uri}")
			actual_queue(uri)

		case "pause", :
			print(f"Pausing playback")
			pause()

		case "resume", :
			print(f"Resuming playback")
			resume()

		case _:
			print("Unknown command")

	return True


if __name__ == '__main__':
	while controller_loop():
		pass

