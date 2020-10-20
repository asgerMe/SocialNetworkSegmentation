import json
import sys
import os
import pickle
from pathlib import Path
from ast import literal_eval

sys.path.append(os.path.join(Path(os.path.abspath("./")).parents[0], 'twitter_graph_iterator'))
sys.path.append(os.path.join(Path(os.path.abspath("./")).parents[0], 'twitter_node_generator'))

from api import twitterAPIWrapper as API

graph = None
CREDENTIALS = None

with open('config.json') as file:
    graph_path = json.load(file)
    if not 'path' in graph_path or not 'creds' in graph_path:
        raise KeyError('The field path must be in graph_path.json')
    path = graph_path['path']
    CREDENTIALS = graph_path['creds']
    graph_file = os.path.join(path, 'graph')

    with open(graph_file, 'rb') as g:
        graph = pickle.load(g)

api = API(CREDENTIALS)
def monte_carlo_sample(screen_name):
    profile = api.get_user_by_screen_name(screen_name=screen_name)
    if 'id' in profile:
        profile_id = profile['id']
    else:
        raise ValueError('Name could not be found !')
    if profile_id in graph.connections:
        print('found it')
    else:
        likes = api.get_likes(profile_id)
        followers = api.get_followers(profile_id)
        following = api.get_following(profile_id)

        print(likes)
        print(followers)
        print(following)
        print('search some more nodes')


monte_carlo_sample('@statsmin')


