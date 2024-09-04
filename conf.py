port = 7000
server_ip = "insert_ip_here"
url = f"http://{server_ip}:{port}"
redirect_uri = url + "/login"
webapp_redirect = f"http://{server_ip}:5000/receive_code"

client_id = "16d4bd814f104e29a21c61f7cb9c022b"
client_secret = "InsertSecretHere"

scope = "user-modify-playback-state user-read-currently-playing user-read-playback-state playlist-modify-public playlist-modify-private "

# In seconds. Needs to be lower than 3600
token_lifetime = 3500

queue_size = 5
# In seconds. Should be lower than the average length of a song
player_loop_time = 10
# The number of times a track needs to be seen in the queue, before it is removed
max_track_count = queue_size * 300 // player_loop_time

default_track_name = "Fireball (feat. John Ryan)"
default_track_uri = "spotify:track:4Y7XAxTANhu3lmnLAzhWJW"

default_playlist_id = "5zFi8YZomeTAbBFfN0Ib4O"
