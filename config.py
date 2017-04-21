import os

class Config(object):
    # these need to be stored as env vars for spotipy to use
    SPOTIPY_REDIRECT_URI = os.environ['SPOTIPY_REDIRECT_URI'] = 'https://www.google.com'
    SPOTIPY_CLIENT_ID = os.environ['SPOTIPY_CLIENT_ID'] = '76159224cd0e4725826934d253118290'
    SPOTIPY_CLIENT_SECRET = os.environ['SPOTIPY_CLIENT_SECRET'] = 'fd3f120077a3491898bb444c5a23beef'
    SPOTIFY_ACCESS_SCOPE = 'user-library-read playlist-read-private playlist-read-public playlist-modify-private'
