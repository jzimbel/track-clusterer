import pprint
import sys
# must import before spotipy to set env vars
from config import Config
import spotipy
from spotipy import util as util
import json
import argparse
import numpy
from sklearn.cluster import DBSCAN
from collections import OrderedDict


FEATURE_NAMES = [
    'acousticness', 'danceability', 'energy', 'instrumentalness',
    'liveness', 'speechiness', 'valence'
]
FEATURES_JSON = 'features.json'


class TrackClusterer(object):
    def __init__(self):
        token = util.prompt_for_user_token(Config.USER_ID, Config.SPOTIFY_ACCESS_SCOPE)
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.sp.trace = False
        else:
            print "Can't get token for", Config.USER_ID
            sys.exit(1)

    def get_library_features(self):
        '''
        Pull track audio features from Spotify.
        Store them in features.json and return them in a dict.
        '''
        feature_dict = self.build_feature_dict()
        with open(FEATURES_JSON, 'w+') as f:
            serializable_feature_dict = [(k, v) for k,v in feature_dict.iteritems()]
            json.dump(serializable_feature_dict, f, indent=2)
        print 'Ordered feature dict stored in {}.'.format(FEATURES_JSON)
        return feature_dict

    def build_feature_dict(self):
        '''
        Returns a dict of track_id: (acousticness, danceability, energy, instrumentalness,
        liveness, speechiness, valence) k/v pairs for all (well, most) tracks in the user's library.
        Some tracks don't have audio features for some reason.
        '''
        # get ids of all tracks in the user's library
        print 'Getting your tracks\' audio features from Spotify...'
        saved_track_ids = []
        results = self.sp.current_user_saved_tracks(limit=50)
        while True:
            items = results['items']
            saved_track_ids.append([item['track']['id'] for item in items])
            if results['next'] == None:
                break
            # let us never speak of this
            next_offset = int(filter(lambda x: x.startswith('offset'), results['next'].split('?')[1].split('&'))[0].split('=')[1])
            results = self.sp.current_user_saved_tracks(limit=50, offset=next_offset)

        # get audio features for each track. Throw out tracks that don't have features.
        feature_dict = OrderedDict()
        for track_id_chunk in saved_track_ids:
            audio_features_response = self.sp.audio_features(tracks=track_id_chunk)
            # only keep values we care about. Ignore feature sets that have null values.
            feature_dict_chunk = {
                item['id']: tuple(item[name] for name in FEATURE_NAMES)
                for item in audio_features_response
                if not any(value is None for value in item.values())
            }
            feature_dict.update(feature_dict_chunk)
        print 'Done! Found {} tracks with audio features in your library.'.format(len(feature_dict.keys()))
        return feature_dict

    def build_cluster_playlists(self, track_id_clusters):
        '''
        Didn't get to this part!
        '''
        print "I would've built Spotify playlists for each cluster here, but I didn't get to that!"


def main(feature_dict):
    '''
    Do clustery things.
    '''
    Config.USER_ID = args.id
    track_clusterer = TrackClusterer()
    if args.infile is None:
        feature_dict = track_clusterer.get_library_features()
    else:
        with open(args.infile) as f:
            feature_dict = OrderedDict([(k, tuple(v)) for k,v in json.load(f)])

    feature_array = numpy.array(feature_dict.values())
    print "Clustering your tracks..."
    cluster = best_clustering(feature_array)
    unique_labels = set([label for label in cluster.labels_ if label != -1])
    print "Done! Your library contains {} clusters.".format(len(unique_labels))
    clustered_track_ids = {label: [] for label in unique_labels}
    for label, track_id in zip(cluster.labels_, feature_dict.keys()):
        if label == -1: continue
        clustered_track_ids[label].append(track_id)

    if args.outfile is None:
        track_clusterer.create_playlists(clustered_track_ids)
    else:
        with open(args.outfile, 'w+') as f:
            json.dump(clustered_track_ids, f, indent=2)
            print "Track clusters stored in {}.".format(args.outfile)


def best_clustering(feature_array):
    '''
    Use DBSCAN to cluster feature_array repeatedly with different epsilon values.
    Return the best clustring based on arbitrary metrics!
    score each clustering on:
    - percentage of features placed in clusters, not marked as noise (maximize)
    - number of clusters (maximize)
    - avg. difference in size of clusters' cores (minimize)
    '''
    scores = []
    results = []
    epsilon_values = [val/100.0 for val in range(10,31)]
    for eps in epsilon_values:
        result = DBSCAN(eps=eps).fit(feature_array)
        results.append(result)

        clustered_count = len(result.labels_) - list(result.labels_).count(-1)
        cluster_counts = {}
        for index in result.core_sample_indices_:
            count = cluster_counts.setdefault(result.labels_[index], 0)
            cluster_counts[result.labels_[index]] = count + 1

        # metric 1
        clustered_label_percentage = clustered_count / float(len(feature_array))
        # metric 2
        n_clusters = len(cluster_counts.keys())
        cluster_size_diffs = []
        cluster_sizes = cluster_counts.values()
        for i, size1 in enumerate(cluster_sizes):
            for size2 in cluster_sizes[i+1:]:
                cluster_size_diffs.append(abs(size1-size2))
        # metric 3
        if len(cluster_size_diffs) == 0:
            # don't want a single cluster anyway
            avg_cluster_size_diff = float('inf')
        else:
            avg_cluster_size_diff = sum(cluster_size_diffs)/float(len(cluster_size_diffs))
        score = (clustered_label_percentage, n_clusters, 1/avg_cluster_size_diff)
        scores.append(score)
    # replace (score1, score2, score3) tuples
    # with (rank_among_score1's, rank_among_score2's, rank_among_score3's) tuples
    ranks = [[] for _ in scores]
    for i in range(3):
        # [(original_index, score)]
        sorted_metrics = sorted(enumerate(map(lambda x: x[i], scores)), key=lambda x:x[1], reverse=True)
        for i, ranking in enumerate(sorted_metrics):
            # [(rank, (original_index, score))]
            ranks[ranking[0]].append(i)
    grand_totals = [sum(rank) for rank in ranks]
    # pick the one with the lowest sum total ranking
    best_index = min(sorted(enumerate(grand_totals), key=lambda x: x[1]), key=lambda x: x[1])[0]
    return results[best_index]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Cluster tracks in your Spotify library by their audio features.' +\
                    '\nThe first time you run this, your library\'s audio features are cached' +\
                    '\nin {}. After that, you can run with fewer Spotify API requests using `python {} {}`'.format(
                        FEATURES_JSON, sys.argv[0], '-f {}'.format(FEATURES_JSON)
                    )
    )
    parser.add_argument('id', help='Your Spotify ID. Instructions for finding your ID: https://community.spotify.com/t5/Accounts/how-do-i-find-my-spotify-user-id/m-p/665688#M86799')
    parser.add_argument('-i', '--infile', help='JSON file to load features from instead of pulling from Spotify')
    parser.add_argument('-o', '--outfile', help='If specified, just output the clustered track names to the given file instead of creating playlists for each cluster.')
    args = parser.parse_args()
    main(args)
