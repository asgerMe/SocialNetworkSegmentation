import json
import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from ast import literal_eval


class MSProfileUser:

    def __init__(self, name, graph, nodegen):
        self.__graph = graph
        self.__inverse_connections = self.invert_connections()
        self.__followers = []

        self.samples = np.asmatrix([0, 0, 0])
        if not isinstance(name, list):
            twitter_info = nodegen.new(name)
            if twitter_info.id in self.__graph.nodes:
                self.profile_node = self.__graph.nodes[twitter_info.id]
            else:
                raise AttributeError('User is not present in graph')
        else:
            for twitter_id in name:
                self.__followers.append(self.__graph.nodes[twitter_id])
                self.profile_node = None

        self.__name = name

    def __call__(self, samples=1000, fsamples=10, discount=0.95):
        if fsamples > 0 and isinstance(self.__name, str):
            self.get_follower_nodes()
            self.get_following_nodes()

        weak_learners = []
        if samples > 0:
            if self.profile_node:
                weak_learners.append(self.monte_carlo(self.profile_node, samples=samples, discount=discount))
            if len(self.__followers) > 0:
                for f in self.__followers:
                    mc_sample = self.monte_carlo(f, samples=fsamples, discount=discount)
                    if len(mc_sample) > 0:
                        weak_learners.append(mc_sample)
        return weak_learners[0]

    def get_follower_nodes(self):
        follow_response = self.profile_node.get_followers(self.profile_node.screen_name)
        if 'users' in follow_response:
            for user in follow_response['users']:
                if user['id_str'] in self.__graph.nodes:
                    self.__followers.append(self.__graph.nodes[user['id_str']])

    def get_following_nodes(self):
        follow_response = self.profile_node.get_following(self.profile_node.screen_name)
        if 'users' in follow_response:
            for user in follow_response['users']:
                if user['id_str'] in self.__graph.nodes:
                    self.__followers.append(self.__graph.nodes[user['id_str']])

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
            distance = np.linalg.norm(np.asarray(parent_feature_vector) - np.asarray(node.feature_vector))

            feature_distances = np.append(feature_distances, distance)
            id_list = np.append(id_list, parent_id)

        return self.pick_parent(feature_distances, id_list)

    def monte_carlo(self, root_node, samples=1, discount=0.4):
        if not root_node:
            raise ValueError('User not found !')

        for s in range(samples):
            node = root_node
            if np.linalg.norm(root_node.feature_vector) == 0:
                return root_node.feature_vector

            feature_vectors = [root_node.feature_vector]
            node_list = [0, 0]
            chain_length = 0

            while node:
                node = self.get_parent_nodes(node)
                if not node or node.id == node_list[-2] or node.id == node_list[-1]:
                    discounts = discount * np.ones(len(feature_vectors))
                    discounts = np.cumprod(discounts)
                    feature_vectors = feature_vectors * np.tile(discounts, (3, 1)).T
                    self.samples = np.concatenate([self.samples, feature_vectors], axis=0)
                    break

                feature_vectors.append(np.asarray(node.feature_vector) * np.exp(
                    -2.0 * np.linalg.norm(np.asarray(root_node.feature_vector) - np.asarray(node.feature_vector))))
                node_list.append(node.id)

                chain_length += 1

        profile_vector = np.asarray(np.mean(self.samples, axis=0))[0]
        return profile_vector / np.sum(np.abs(profile_vector))

    def show(self):
        if len(self.samples) == 0:
            return None
        fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)
        axs[0].hist(self.samples[:, 0], bins=200)
        axs[1].hist(self.samples[:, 1], bins=200)
        axs[2].hist(self.samples[:, 2], bins=200)
        plt.show()

