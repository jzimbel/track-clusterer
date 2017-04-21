import pprint
import sys
# must import before spotipy to set env vars
from config import Config
import spotipy
from spotipy import util as util
import json
import argparse
import numpy
from sklearn.cluster import KMeans
from collections import OrderedDict


feature_names = [
    'acousticness', 'danceability', 'energy', 'instrumentalness',
    'liveness', 'speechiness', 'valence'
]
features_json = 'features.json'


def main(feature_dict):
    '''
    Do clustering things.
    '''
    feature_array = numpy.array(feature_dict.values())
    n_clusters = 8
    result = KMeans(n_clusters=n_clusters, init='k-means++').fit(feature_array)
    track_id_clusters = {label: [] for label in range(n_clusters)}
    track_ids = feature_dict.keys()
    for i, label in enumerate(result.labels_):
        track_id_clusters[label].append(track_ids[i])
    # build playlists for each cluster


def get_library_features():
    '''
    Pull track audio features from Spotify.
    Store them in features.json and return them in a dict.
    '''
    token = util.prompt_for_user_token(Config.USER_ID, Config.SPOTIFY_ACCESS_SCOPE)
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        feature_dict = build_feature_dict(sp)
        with open(features_json, 'w+') as f:
            serializable_feature_dict = [(k, v) for k,v in feature_dict.iteritems()]
            json.dump(serializable_feature_dict, f, indent=2)
        print 'Ordered feature dict stored in {}.'.format(features_json)
        return feature_dict
    else:
        print "Can't get token for", Config.USER_ID


def build_feature_dict(sp):
    '''
    Returns a dict of track_id: (acousticness, danceability, energy, instrumentalness,
    liveness, speechiness, valence) k/v pairs for all (well, most) tracks in the user's library.
    Some tracks don't have audio features for some reason.
    '''
    # get ids of all tracks in the user's library
    print 'Getting your tracks\' audio features from Spotipy...'
    saved_track_ids = []
    results = sp.current_user_saved_tracks(limit=50)
    while True:
        items = results['items']
        saved_track_ids.append([item['track']['id'] for item in items])
        if results['next'] == None:
            break
        # let us never speak of this
        next_offset = int(filter(lambda x: x.startswith('offset'), results['next'].split('?')[1].split('&'))[0].split('=')[1])
        results = sp.current_user_saved_tracks(limit=50, offset=next_offset)

    # get audio features for each track. Throw out tracks that don't have features.
    feature_dict = OrderedDict()
    for track_id_chunk in saved_track_ids:
        audio_features_response = sp.audio_features(tracks=track_id_chunk)
        # only keep values we care about. Ignore feature sets that have null values.
        feature_dict_chunk = {
            item['id']: tuple(item[name] * 100 for name in feature_names)
            for item in audio_features_response
            if not any(value is None for value in item.values())
        }
        feature_dict.update(feature_dict_chunk)
    print 'Done! Found {} tracks with audio features in your library.'.format(len(feature_dict.keys()))
    return feature_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Cluster tracks in your Spotify library by their audio features.' +\
                    '\nThe first time you run this, your library\'s audio features are cached' +\
                    '\nin {}. After that, you can run without talking to Spotify using `python {} {}`'.format(
                        features_json, sys.argv[0], '-f {}'.format(features_json)
                    )
    )
    parser.add_argument('-i', '--id', help='Your Spotify ID. Instructions for finding your ID: https://community.spotify.com/t5/Accounts/how-do-i-find-my-spotify-user-id/m-p/665688#M86799')
    parser.add_argument('-f', '--file', help='JSON file to load features from instead of pulling from Spotify')
    args = parser.parse_args()

    if args.id is None and args.file is None:
        print 'Error: Either a Spotify ID or a JSON features file must be provided.'
        print 'See help with `python {} -h`'.format(sys.argv[0])
        sys.exit(1)

    if args.file is None:
        Config.USER_ID = args.id
        main(get_library_features())
    else:
        feature_dict = None
        with open(args.file) as f:
            feature_dict = OrderedDict([(k, tuple(v)) for k,v in json.load(f)])
        main(feature_dict)
