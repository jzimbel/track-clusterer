import pprint
import sys
import spotipy
import spotipy.util as util

from config import Config

feature_names = [
    'acousticness', 'danceability', 'energy', 'instrumentalness',
    'liveness', 'speechiness', 'valence'
]

def main():
    token = util.prompt_for_user_token(Config.USER_ID, Config.SPOTIFY_ACCESS_SCOPE)
    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        feature_list = build_feature_list(sp)
        # now do AI things!!! EZPZ
    else:
        print "Can't get token for", Config.USER_ID


def chunk(l, n):
    '''
    Generator. Yields n-size slices of the provided list.
    Useful for making requests to API endpoints that limit query length.
    '''
    for i in range(0, len(l), n):
        yield l[i:i + n]


def feature_as_list(feature):
    '''
    Produce a list from a feature dict in the order of feature_names. (omits track id)
    '''
    return [feature[name] for name in feature_names]


def feature_distance(feature1, feature2):
    '''
    Calculate the Euclidean distance between two features.
    features must be tuples in the order:
    (acousticness, danceability, energy, instrumentalness, liveness, speechiness, valence)
    '''
    # sqrt((p1-q1)**2 + (p2-q2)**2 + ...)
    return sum(map(lambda x: (x[1] - x[0])**2, zip(feature1, feature2)))**0.5


def cluster(feature_list):
    '''
    Maybe use scikit-learn's cluster function?
    '''
    pass


def build_feature_list(sp):
    '''
    Returns a list of feature dicts for all (well, most) tracks in the user's library.
    Some tracks don't have audio features for some reason.
    '''
    # get ids of all tracks in the user's library
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
    feature_names_with_id = ['id'] + feature_names
    feature_list = []
    for track_id_chunk in saved_track_ids:
        audio_features_response = sp.audio_features(tracks=track_id_chunk)
        # only keep keys we care about. Ignore feature sets that have null values.
        feature_list_segment = [
            {
                name: item[name]
                for name in feature_names_with_id
            }
            for item in audio_features_response
            if not any(value is None for value in item.values())
        ]
        feature_list.extend(feature_list_segment)

    return feature_list


if __name__ == '__main__':
    Config.USER_ID = raw_input('Enter your Spotify User ID: ')
    main()
