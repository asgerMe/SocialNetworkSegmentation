from source.twitter_graph_iterator.iterator import GraphIterator
from source.twitter_node_generator.node_generator import NodeGenerator
from pathlib import Path
from ast import literal_eval

import pickle
import os
import sys
import argparse

default_path = os.path.join(Path(os.path.abspath("./")).parents[0], 'data/graph')

parser = argparse.ArgumentParser()
parser.add_argument('-path', dest='path', type=str, required=False, default=default_path)
args = parser.parse_args()
graph = None

try:
    stored_graph = open(args.path, 'rb')
    if stored_graph is not None:
        graph = pickle.load(stored_graph)
except FileNotFoundError:
    pass

with open(os.path.join(Path(os.path.abspath("./")).parents[0], 'twitter_creds/creds.txt'), 'r') as file:
    CREDENTIALS = literal_eval(file.read())
    if not graph:
        graph_iterator = GraphIterator(NodeGenerator(CREDENTIALS), seed_names=['@RasmusJarlov'])
    else:
        graph_iterator = graph
    for i in range(20):
        graph_iterator.next()
        print(len(graph_iterator.nodes.keys()))

    write_file = open(args.path, 'wb')
    pickle.dump(graph_iterator, write_file)



