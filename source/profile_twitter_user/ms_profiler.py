import json
import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from ast import literal_eval
from scipy.stats import multivariate_normal

class MSProfileUser:

    def __init__(self, name, graph, nodegen):
        self.__graph = graph
        self.__inverse_connections = self.invert_connections()
        self.__followers = []

        self.parties = []
        self.economy = []
        self.immigration = []
        self.climate = []
        self.samples = np.asmatrix([0, 0, 0])
        if not isinstance(name, list):
            twitter_info = nodegen.new(name)
            if twitter_info.id in self.__graph.nodes:
                self.profile_node = self.__graph.nodes[twitter_info.id]
            else:
                raise ValueError('Warning - Profile not found in graph - additional feature propagation might be required !')

        else:
            for twitter_id in name:
                self.__followers.append(self.__graph.nodes[twitter_id])
                self.profile_node = None

        self.__name = name

    def __call__(self, samples, fsamples, discount=0.85):
        if fsamples > 0 and isinstance(self.__name, str):
            self.get_follower_nodes()
            self.get_following_nodes()

        weak_learners = np.asarray([0.0, 0.0, 0.0])
        n = 1
        if samples > 0:
            if self.profile_node:
                weak_learners = self.monte_carlo(self.profile_node, samples=samples, discount=discount)
        if fsamples > 0:
            if len(self.__followers) > 0:
                for f in self.__followers:
                    print(f.name)
                    mc_sample = self.monte_carlo(f, samples=fsamples, discount=discount)
                    if len(mc_sample) > 0:
                        weak_learners += mc_sample
                        n += 1
        weak_learners = weak_learners / n
        QDA_result, keys = self.QDA(weak_learners)

        print('BEST SCORE', weak_learners, keys[np.argmax(QDA_result)], str(np.round(100*QDA_result[np.argmax(QDA_result)])) + '%')

        sorted_idx = np.argsort(QDA_result)

        for qdaidx in sorted_idx[-3:]:
            print(keys[qdaidx], str(np.round(100*QDA_result[qdaidx])) + '%')

        print(QDA_result, keys)
        return weak_learners

    def check_likes_for_party_affiliation(self, node, feature_list):
        if node.id not in self.__graph.connections:
            return feature_list

        for c_node_id in self.__graph.connections[node.id]:
            feature_list[node.party].append( self.__graph.nodes[c_node_id].feature_vector)
        return feature_list

    def QDA(self, profile_feature):
        party_features = dict(ALL=[])
        for node_id in self.__graph.nodes:
            node = self.__graph.nodes[node_id]
            if node and node.party:
                if not node.party in party_features:
                    party_features[node.party] = [node.feature_vector]
                else:
                    party_features[node.party].append(node.feature_vector)
                party_features = self.check_likes_for_party_affiliation(node, party_features)
            else:
                party_features['ALL'].append(node.feature_vector)

        pxk_pk = []
        party_names = []
        n = 0

        for party_key, party_feature in party_features.items():
            if party_key == 'ALL':
                continue
            n += np.shape(party_feature)[0]

        for party_key, party_feature in party_features.items():
            if party_key == 'ALL':
                continue
            feature_mean, feature_covariance = self.get_mean_and_covariance(party_feature)
            print(feature_mean, profile_feature, np.linalg.norm(feature_mean - profile_feature), party_key)
            Nk = multivariate_normal(feature_mean, feature_covariance)
            pxk_pk.append(Nk.pdf(profile_feature)*np.shape(party_feature)[0]/n)
            party_names.append(party_key)

        return np.asarray(pxk_pk) / np.sum(pxk_pk), party_names

    def get_mean_and_covariance(self, features):
        feature = np.asarray(features)
        feature_mean = np.mean(features, axis=0)
        feature_covariance = np.cov(feature.T)

        return feature_mean, feature_covariance

    def get_follower_nodes(self):
        follow_response = self.profile_node.get_followers(self.profile_node.screen_name)
        if 'users' in follow_response:
            for user in follow_response['users']:
                if user['id_str'] in self.__graph.nodes:
                    print(user['name'])
                    self.__followers.append(self.__graph.nodes[user['id_str']])

    def get_following_nodes(self):
        follow_response = self.profile_node.get_following(self.profile_node.screen_name)
        if 'users' in follow_response:
            for user in follow_response['users']:
                if user['id_str'] in self.__graph.nodes:
                    print(user['name'])
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

    def monte_carlo(self, root_node, samples=1, discount=0.95):
        if not root_node:
            raise ValueError('User not found !')

        for s in range(samples):
            node = root_node
            if np.linalg.norm(root_node.feature_vector) == 0:
                return root_node.feature_vector

            feature_vectors = [root_node.feature_vector]
            self.samples = np.concatenate([self.samples, np.asmatrix(root_node.feature_vector)], axis=0)
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

                feature_vectors.append(np.asarray(node.feature_vector))
                node_list.append(node.id)
                chain_length += 1

        RESULT =  np.asarray(np.mean(self.samples, axis=0))[0]
        RESULT = RESULT / (0.000001 + np.linalg.norm(RESULT))
        return RESULT


    def show(self):
        if len(self.samples) == 0:
            return None
        fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)
        axs[0].hist(self.samples[:, 0], bins=200)
        axs[1].hist(self.samples[:, 1], bins=200)
        axs[2].hist(self.samples[:, 2], bins=200)
        plt.show()

