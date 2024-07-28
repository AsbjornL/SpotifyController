from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from base64 import b64encode
from time import time
import requests
import conf
import json


access_token = ""
refresh_token = ""
token_time = 0
playlist_id = ""
device_id = ""
queue_id = ""

paused = False
stop_playback = False


class RequestHandler(BaseHTTPRequestHandler):    
    def text_response(self, text):
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        if parsed_path.path == '/':
            self.send_response(200)
            self.text_response("Hello World")

        elif parsed_path.path == '/login':
            if code := params.get('code', [''])[0]:
                m = f"code received: {code}"
                self.send_response(200, message=m)
                self.text_response(m)

                get_access_token(code)

            else:
                self.send_response(400, message="No code given")
                self.text_response("Request received, but no code given")
                print("/login: Request received, but no code given")
        
        elif parsed_path.path == '/token':
            if time() - token_time >= conf.token_lifetime:
                refresh_access_token()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('token', access_token)
            self.end_headers()
            self.wfile.write(json.dumps({'token': access_token}).encode('utf-8'))

        elif parsed_path.path == '/stop':
            self.send_response(200)
            print("Shutting down")
            self.server.shutdown()
        
        elif parsed_path.path == '/playlist_id':
            if playlist_id:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('id', playlist_id)
                self.end_headers()
                self.wfile.write(json.dumps({'id': playlist_id}).encode('utf-8'))
            else:
                self.send_response(204)
                self.text_response("No playlist_id set")

        elif parsed_path.path == '/device_id':
            if device_id:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('id', device_id)
                self.end_headers()
                self.wfile.write(json.dumps({'id': device_id}).encode('utf-8'))
            else:
                self.send_response(204)
                self.text_response("No device_id set")

        elif parsed_path.path == '/queue_id':
            if queue_id:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('id', queue_id)
                self.end_headers()
                self.wfile.write(json.dumps({'id': queue_id}).encode('utf-8'))
            else:
                self.send_response(204)
                self.text_response("No queue_id set")

        elif parsed_path.path == '/info':
            if time() - token_time >= conf.token_lifetime:
                refresh_access_token()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('qid', queue_id)
            self.send_header('did', device_id)
            self.send_header('pid', playlist_id)
            self.send_header('token', access_token)
            self.send_header('stop', stop_playback)
            self.end_headers()
            self.wfile.write(json.dumps({
                'qid': queue_id,
                'did': device_id,
                'pid': playlist_id,
                'token': access_token,
                'stop': stop_playback
            }).encode('utf-8'))

        elif parsed_path.path == '/paused':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('paused', paused)
            self.end_headers()
            self.wfile.write(json.dumps({
                'paused': paused,
            }).encode('utf-8'))

        else:
            self.send_response(404)
            self.text_response("404 Not Found")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        parsed_data = parse_qs(post_data.decode('utf-8'))

        if self.path == '/set_playlist':
            if id := parsed_data.get('id', [""])[0]:
                self.send_response(200)
                global playlist_id
                playlist_id = id
                self.text_response(f"Set playlist id to: id")
            
            else:
                self.send_response(400, message="No id given")
                self.text_response("No playlist id given")

        elif self.path == '/device_id':
            if did := parsed_data.get('id', [""])[0]:
                self.send_response(200)
                global device_id
                device_id = did
                self.text_response(f"Set device id to: {did}")
            
            else:
                self.send_response(400, message="No id given")
                self.text_response("No device id given")

        elif self.path == '/queue_id':
            if qid := parsed_data.get('id', [""])[0]:
                self.send_response(200)
                global queue_id
                queue_id = qid
                self.text_response(f"Set queue id to: {qid}")
            
            else:
                self.send_response(400, message="No id given")
                self.text_response("No device id given")

    def do_PUT(self):
        global paused
        global stop_playback
        if self.path == '/pause':
            self.send_response(200)
            self.text_response("Paused")
            paused = True

        elif self.path == '/resume':
            self.send_response(200)
            self.text_response("Resuming")
            paused = False

        elif self.path == '/stop_player':
            stop_playback = True
            self.send_response(200)
            self.text_response("Stopping player")

        elif self.path == '/start_player':
            stop_playback = False
            self.send_response(200)
            self.text_response("Player no longer stopped")


def refresh_access_token():
    print("Refreshing access token")
    global refresh_token
    url = "https://accounts.spotify.com/api/token"
    fields = {
        'grant_type': "refresh_token",
        'refresh_token': refresh_token,
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Basic " + b64encode(f"{conf.client_id}:{conf.client_secret}".encode()).decode()
    }

    response = requests.post(url, data=fields, headers=headers)

    if response.status_code != 200:
        print(f"Refreshing access token failed: {response.reason}")
        raise Exception
    else:
        res_json = response.json()
        global access_token
        access_token = res_json.get("access_token")
        global token_time
        token_time = time() 


def get_access_token(code):
    url = "https://accounts.spotify.com/api/token"
    fields = {
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': conf.redirect_uri
    }
    headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'Authorization': "Basic " + b64encode(f"{conf.client_id}:{conf.client_secret}".encode()).decode()
    }

    response = requests.post(url, data=fields, headers=headers)

    if response.status_code != 200:
        print(f"Getting access token failed: {response.reason}")
        raise Exception
    else:
        res_json = response.json()
        global access_token
        access_token = res_json.get("access_token")
        global refresh_token
        refresh_token = res_json.get("refresh_token")
        global token_time
        token_time = time()


def run(server_class=HTTPServer, handler_class=RequestHandler, port=conf.port):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

