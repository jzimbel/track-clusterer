import os

class Config(object):
    # these need to be stored as env vars for spotipy to use
    SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.google.com'
    SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID'] = '76159224cd0e4725826934d253118290'
    SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET'] = 'fd3f120077a3491898bb444c5a23beef'
    SPOTIFY_ACCESS_SCOPE = 'user-library-read'

    ###########
    # Options #
    ###########

    # TRACKS_PER_ARTIST #
    # Number of tracks per artist to add to the playlist.
    # I recommend 5 or less. Max is 10.
    TRACKS_PER_ARTIST = 3

    # COLLATE #
    # By default, the playlist will be ordered like:
    # - ARTIST A TRACK 1
    # - ARTIST A TRACK 2
    # - ARTIST A TRACK 3
    # - ARTIST A TRACK 4
    # - ARTIST A TRACK 5
    # - ARTIST B TRACK 1
    # - ARTIST B TRACK 2
    # - ARTIST B TRACK 3
    # ...

    # if COLLATE is set to True, it will instead be ordered like so:
    # - ARTIST A TRACK 1
    # - ARTIST B TRACK 1
    # - ARTIST C TRACK 1
    # ...
    # - ARTIST Z TRACK 1
    # - ARTIST A TRACK 2
    # - ARTIST B TRACK 2
    # ...
    COLLATE = False

    # PUBLIC #
    # Default False. Set True to make your generated playlist public.
    PUBLIC = True
