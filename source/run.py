import sys
import os
from pathlib import Path
import time

web_path = os.path.join(Path(os.path.abspath("./")).parents[0], 'web')
sys.path.append(os.path.join(os.getcwd(), 'twitter_graph_iterator'))
sys.path.append(os.path.join(os.getcwd(), 'twitter_node_generator'))
sys.path.append(os.path.join(os.getcwd(), 'profile_twitter_user'))
sys.path.append(web_path)
sys.path.append(os.path.join(os.getcwd(), 'pbd_graph_iterator'))

from iterator import GraphIterator
from node_generator import NodeGenerator
from api import twitterAPIWrapper
from ms_profiler import MSProfileUser

from pbd_graph_iterator import pbditerator
from render_website import render

from pathlib import Path
from ast import literal_eval

import pickle
import argparse

import numpy as np

default_path = Path(os.path.abspath("./")).parents[0]

parser = argparse.ArgumentParser()
parser.add_argument('--path', dest='path', type=str, required=False, default=default_path)
parser.add_argument('--iter', dest='iterations', type=int, required=False, default=0)
parser.add_argument('--names', nargs='+', dest='names', required=False, default=[])
parser.add_argument('--pbditer', dest='pbditer', required=False, default=0, type=int)
parser.add_argument('--profile', dest='profile', required=False, default='', type=str)
parser.add_argument('--mcsamples', dest='mcsamples', required=False, default=500, type=int)
parser.add_argument('--fmcsamples', dest='fmcsamples', required=False, default=100, type=int)
parser.add_argument('-show', dest='show', action='store_true')
parser.add_argument('--partyprofile', dest='partyprofile', action='store_true')
parser.add_argument('--setparty', dest='setparty', type=str, default='')
parser.add_argument('-add', '--addnodes', nargs='+', dest='addnodes', required=False)
args = parser.parse_args()
graph = None
graph_iterator = None

try:
    stored_graph = open(os.path.join(args.path, 'data/graph'), 'rb')
    if stored_graph is not None:
        graph = pickle.load(stored_graph)
except FileNotFoundError:
    pass

with open(os.path.join(Path(os.path.abspath("./")).parents[0], 'twitter_creds/creds.txt'), 'r') as file:
    CREDENTIALS = literal_eval(file.read())
    if len(args.names) == 0:
        names = ['@Spolitik',
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
                 '@veganerpartiet',
                 "@KDDanmark",
                 ]
    else:
        names = args.names
    if not graph:
        graph_iterator = GraphIterator(NodeGenerator(CREDENTIALS), seed_names=names)
    else:
        graph_iterator = graph

    if args.addnodes and len(args.addnodes) > 0:
        for node_handle in args.addnodes:
            graph_iterator.expand_graph(node_handle)

    if args.iterations > 0:
        while True:
            for i in range(args.iterations):
                graph_iterator.next()
                print('ITERATION: {}'.format(i))
                print('Progress: {} %'.format((1+i) / args.iterations*100))
                print('Graph Size: {}'.format(len(graph_iterator.nodes.keys())))
                print('------------')

            write_file = open(os.path.join(args.path, 'data/graph'), 'wb')
            pickle.dump(graph_iterator, write_file)
            write_file.close()

            time.sleep(1800)

if args.pbditer > 0:
    pbd_iterator = pbditerator.PbdGraphIterator(graph_iterator)
    pbd_iterator(iterations=int(args.pbditer))

    write_file = open(os.path.join(args.path, 'data/graph'), 'wb')
    pickle.dump(pbd_iterator.graph, write_file)
    write_file.close()
    render(pbd_iterator.graph)

if args.profile != '' and args.setparty == '':
    profiler = MSProfileUser(name=args.profile, graph=graph, nodegen=NodeGenerator(CREDENTIALS))
    profile_feature = profiler(samples=args.mcsamples, fsamples=args.fmcsamples)


    if args.show:
        profiler.show()

if args.partyprofile:
    payload = []
    party_members = []
    for node_id in graph.nodes:
        node = graph.nodes[node_id]
        if node.party:
            payload.append(node.id)
            party_members.append(node.name)

    profiler = MSProfileUser(name=payload, graph=graph, nodegen=NodeGenerator(CREDENTIALS))
    E = profiler(samples=args.mcsamples, fsamples=args.fmcsamples)

    if args.show:
        profiler.show()

if args.setparty != '' and args.profile != '':
    node = NodeGenerator(CREDENTIALS).new(args.profile, args.setparty)
    if not node.id in graph.nodes:
        raise ValueError('Profile not found in graph')

    write_file = open(os.path.join(args.path, 'data/graph'), 'wb')
    pickle.dump(graph, write_file)
    write_file.close()










