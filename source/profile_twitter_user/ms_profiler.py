import json
import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from ast import literal_eval


class MSProfileUser:

    def __init__(self, graph, nodegen):
        self.__inverse_connections = self.invert_connections()
        self.__nodegen = nodegen
        self.__graph = graph

    def invert_connections(self):
        inverse = {}
        for i in self.__graph.connections:
            for j in self.__graph.connections[i]:
                if not j in inverse:
                    inverse[j] = []
                inverse[j].append(i)
        return inverse

    def get_parents(self, node):
        if not node.id in self.__inverse_connections:
            return None

        parents = self.__inverse_connections[node.id]
        if len(parents) == 0:
            return None

        return parents

    def pick_parent(self, feature_distances, id_list):
        sorted_ids = np.argsort(feature_distances)
        id_list = id_list[sorted_ids]
        max_feature_length = np.max(feature_distances)
        if max_feature_length == 0:
            feature_distances[0] = 1.0
        else:
            feature_distances = feature_distances[sorted_ids] / max_feature_length

        r_int = np.random.rand()
        return self.__graph.nodes[id_list[feature_distances > r_int][0]]


    def get_parent_nodes(self, node):
        feature_distances = np.asarray([])
        id_list = np.asarray([])
        parents = self.get_parents(node)

        if not parents:
            return None

        for parent_id in parents:
            parent_feature_vector = self.__graph.nodes[parent_id].feature_vector
            distance = np.linalg.norm(parent_feature_vector - node.feature_vector)

            feature_distances.append(distance)
            id_list.append(parent_id)

        return self.pick_parent(feature_distances, id_list)


'''
def get_followers(profile_id, inv_connections):
    followers = api.get_followers(profile_id)
    followers_ids = []
    if 'users' in followers and len(followers['users']) == 0:
        return False

    if not profile_id in graph.connections:
        graph.connections[profile_id] = {}

    if 'users' in followers:
        for user in followers['users']:
            follower_id = user['str_id']
            followers_ids.append(follower_id)
    return followers_ids

def monte_carlo_sample(screen_name, samples=1, discount=0.8, cutoff=20000):
    SAMPLES = []
    PARTIES = []

    profile = api.get_user_by_screen_name(screen_name=screen_name)
    inv_connections = invert_connections(graph)
    followers = get_followers(screen_name, inv_connections)
    node_generator = NodeGenerator(CREDENTIALS)

    if 'id' in profile:
        profile_id = profile['id_str']
    else:
        raise ValueError('Name could not be found !')

    for s in range(samples):
        node = graph.nodes[profile_id]
        root_node = node

        feature_vectors = [root_node.feature_vector]
        node_list = [0, 0, 0]
        chain_length = 0
        while node:
            node = pick_parent_node(node, inv_connections)
            if node and node.party:
                PARTIES.append({'name': node.party, 'val': pow(discount, chain_length)})
            if not node or node.id == node_list[-2] or node.id == node_list[-1] :
                discounts = discount*np.ones(len(feature_vectors))
                discounts = np.cumprod(discounts)
                feature_vectors = feature_vectors*np.tile(discounts, (3, 1)).T
                SAMPLES.append(np.sum(feature_vectors, 0))
                break

            feature_vectors.append(np.asarray(node.feature_vector)*np.exp(-2.0*np.linalg.norm(root_node.feature_vector-node.feature_vector)))
            node_list.append(node.id)

            if chain_length > cutoff:
                break
            chain_length += 1
    SAMPLES = np.asmatrix(SAMPLES)

    party_scores = {}
    for party in PARTIES:
        if party['name'] in party_scores:
            party_scores[party['name']] += party['val']
        else:
            party_scores[party['name']] = party['val']

    print(party_scores)

    fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)

    axs[0].hist(SAMPLES[:, 0])
    axs[1].hist(SAMPLES[:, 1])
    axs[2].hist(SAMPLES[:, 2])
    plt.show()

    monte_carlo_sample('@eltorodk')
'''




