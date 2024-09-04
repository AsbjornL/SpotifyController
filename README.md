# SpotifyController
This project is for adding a interface to control Spotify playback, that is complex and has few options for the user.

To set it up, first create a Spotify app, with `<conf.url>/login` set as a redirect url.

Set the client id, client secret, and the url and port this project should run on in `conf.py`

To run, first run `main.py`.
This will open a server that will connect the different components, and handle access tokens.

Next run `autherize.py`.
This will open a Spotify authorization tab in your browser, asking for permissions.
You can close this, once it says "Code: <access code>"

Now run `player.py`.
This will start the playing session, by asking you for a device to play from.
It will continuously add tracks to a "queue" (that is actually a playlist) that it plays from, ensuring no song is added more than once.
Songs are said to be the same, if their name is an exact match.

If you run `controller.py`, you'll be able to control the playback.
Use any of the following commands

To skip to the next track

```> skip```

To print the tracks currently in the queue, along with their uri's

```> print queue```

To remove a track from the queue. To find the `uri` of a song, use `print queue`

```> remove <uri>```

To add a song as the next in queue. To find the `uri` of a song, right click it on spotify, hover "Share" and hold "alt" and click "Copy Spotify URI".

```> queue <uri>```

To change playlist tracks are chosen from

```> playlist```

To stop the controller

```> exit```

## Todo

- Test in a live setting

- Consider a better default behaviour, than playing Fireball on repeat

- Fuck der er dårlig responstid (skyldes muligvis lort eduroam)

- Add exponential retry behaviour

- Sange i kø-playlisten, men ikke i køen?

- Undersøg følgende adfærd:
	Ved opstart, spillede en sang i 10 sekunder, indtil den blev slettet fra playlisten.
	Herefter blev en ny sang tilføjet til playlisten som spotify begyndte at spille i stedet.
	Problemet blev fikset ved at tilføje endnu en sang til playlisten.
	Idé: Spotify kan ikke lide man lytter til en tom playliste?
