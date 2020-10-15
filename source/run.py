import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'twitter_graph_iterator'))
sys.path.append(os.path.join(os.getcwd(), 'twitter_node_generator'))
sys.path.append(os.path.join(os.getcwd(), 'feature_mapping'))

from iterator import GraphIterator
from node_generator import NodeGenerator
from featuremap import get_node_features

from pathlib import Path
from ast import literal_eval

import pickle
import argparse

default_path = os.path.join(Path(os.path.abspath("./")).parents[0], 'data/graph')

parser = argparse.ArgumentParser()
parser.add_argument('-path', dest='path', type=str, required=False, default=default_path)
parser.add_argument('-iter', dest='iterations', type=int, required=False, default=0)
parser.add_argument('-names', nargs='+', dest='names', required=False, default=[])
parser.add_argument('-featuremap', dest='featuremap', required=False, default=False, type=bool)
args = parser.parse_args()
graph = None
graph_iterator = None

try:
    stored_graph = open(args.path, 'rb')
    if stored_graph is not None:
        graph = pickle.load(stored_graph)
except FileNotFoundError:
    pass

if args.featuremap:
    get_node_features.get_feature_map()


with open(os.path.join(Path(os.path.abspath("./")).parents[0], 'twitter_creds/creds.txt'), 'r') as file:
    CREDENTIALS = literal_eval(file.read())
    if len(args.names) == 0:
        names = ['@Spotlik',
                 '@NyeBorgerlige',
                 '@DanskDf1995',
                 '@KonservativeDK',
                 '@venstredk',
                 '@radikale',
                 '@LiberalAlliance',
                 '@SFpolitik',
                 '@Enhedslisten',
                 '@alternativet_',
                 '@friegronne',
                 '@veganerpartiet'
                 ]
    else:
        names = args.names
    if not graph:
        graph_iterator = GraphIterator(NodeGenerator(CREDENTIALS), seed_names=names)
    else:
        graph_iterator = graph
    for i in range(args.iterations):
        graph_iterator.next()
        print('ITERATION: {}'.format(i))
        print('Progress: {} %'.format((1+i) / args.iterations*100))
        print('Graph Size: {}'.format(len(graph_iterator.nodes.keys())))
        print('------------')

    write_file = open(args.path, 'wb')
    pickle.dump(graph_iterator, write_file)



