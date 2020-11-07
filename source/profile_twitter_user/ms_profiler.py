import json
import sys
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from ast import literal_eval
from scipy.stats import multivariate_normal
import naive_bayes_profiler


PRIOR_ = {
  "@Enhedslisten": 0.069,
  "@alternativet": 0.01,
  "@friegronne": 0.01,
  "@veganerpartiet": 0.008,
  "@radikale": 0.068,
  "@SFpolitik": 0.077,

  "@Spolitik": 0.30,
  "@venstredk": 0.189,
  "@KonservativeDK": 0.095,
  "@DanskDf1995": 0.065,
  "@LiberalAlliance": 0.023,
  "@KDDanmark": 0.017,
  "@NyeBorgerlige": 0.06
}

class MSProfileUser:

    def __init__(self, name, graph):

        self.__graph = graph
        self.__inverse_connections = self.invert_connections()
        self.__followers = []

        self.parties = []
        self.economy = []
        self.immigration = []
        self.climate = []
        self.samples = np.asmatrix([0, 0, 0])

        self.chain_users = []
        self.chain_target_node = None
        self.chain_target_id = None
        self.feature_party = None

        self.naive_bayes_result = None
        self.affiliation_list = self.load_affiliation_list(os.path.join(os.path.abspath(".."), 'data/affiliation_list.json'))

        try:
            self.naive_bayes_classifier = naive_bayes_profiler.NaiveBayesClassifier(name, graph)
            self.naive_bayes_result = self.naive_bayes_classifier()
        except:
            pass

        if not isinstance(name, list):
            if name in self.__graph.nodes:
                self.profile_node = self.__graph.nodes[name]
            else:
                raise ValueError('Warning - Profile not found in graph - additional feature propagation might be required !')
        else:
            for twitter_id in name:
                self.__followers.append(self.__graph.nodes[twitter_id])
                self.profile_node = None

        self.__name = name

    def __call__(self, samples, fsamples, discount=0.85, search_connection=None):
        if search_connection in self.__graph.nodes:
            self.chain_target_node = self.__graph.nodes[search_connection]
        if fsamples > 0 and isinstance(self.__name, str):
            self.get_follower_nodes()
            self.get_following_nodes()

        feature = np.asarray([0.0, 0.0, 0.0])
        n = 1
        if samples > 0:
            if self.profile_node:
                feature = self.monte_carlo(self.profile_node, samples=samples, discount=discount)
        if fsamples > 0:
            if len(self.__followers) > 0:
                for f in self.__followers:
                    mc_sample = self.monte_carlo(f, samples=fsamples, discount=discount)
                    if len(mc_sample) > 0:
                        feature += mc_sample
                        n += 1
        feature = np.asarray(feature) / n

        if self.naive_bayes_result is not None and len(self.naive_bayes_result) > 0 and self.naive_bayes_result[-1] in self.affiliation_list:
            bayes_feature = self.affiliation_list[self.naive_bayes_result[-1]][0]
            bayes_vector = np.asarray([bayes_feature['eco'], bayes_feature['img'], bayes_feature['cli']])
            bayes_vector = bayes_vector / np.linalg.norm(bayes_vector)
            feature += bayes_vector*0.25
        else:
            self.naive_bayes_result = [False]

        QDA_result, keys = self.QDA(feature)
        max_likelihood = self.generate_result(keys, QDA_result)
        return max_likelihood

    def generate_result(self, keys, QDA_result):
        sorted_idx = np.argsort(QDA_result)
        skey = keys[sorted_idx]
        sQDA = QDA_result[sorted_idx]

        print("--# QDA Result #--")
        for name, score in zip(skey[-3:], sQDA[-3:]):
            print(name, str(score*100)[0:4] + '%')
        print('--------------------')
        print( "--# Naive Bayes Result #--")
        if isinstance(self.naive_bayes_result, list) and len(self.naive_bayes_result) > 0:
            print(self.naive_bayes_result[-1])
        else:
            print('No text in profile')
        print('--------------------')
        party_names, count = np.unique(self.feature_party, return_counts=True)
        party_names = party_names[np.argsort(count)]

        print("--# Greedy Result #--")

        if not party_names[-1] in self.affiliation_list and len(party_names) > 1:
            pname = party_names[-2]
            print(party_names[-2])
        else:
            pname = party_names[-1]
            print(party_names[-1])

        if pname == skey[-1] or skey[-1] == self.naive_bayes_result[-1]:
            return skey[-1]
        if pname == self.naive_bayes_result[-1] and (pname == skey[-1] or pname == skey[-2] or pname == skey[-3]):
            return self.naive_bayes_result[-1]
        else:
            return None

    def check_likes_for_party_affiliation(self, node, feature_list):
        if node.id not in self.__graph.connections:
            return feature_list

        for c_node_id in self.__graph.connections[node.id]:
            feature_list[node.party].append(self.__graph.nodes[c_node_id].feature_vector)
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
            if np.linalg.det(feature_covariance) == 0:
                continue
            Nk = multivariate_normal(feature_mean, feature_covariance)
            pxk_pk.append(Nk.pdf(profile_feature)*PRIOR_[party_key])
            party_names.append(party_key)

        return np.asarray(pxk_pk) / np.sum(pxk_pk), np.asarray(party_names)

    def get_mean_and_covariance(self, features):
        feature = np.asarray(features)
        feature_mean = np.mean(features, axis=0)
        feature_covariance = np.cov(feature.T)
        return feature_mean, feature_covariance

    def get_follower_nodes(self):
        follow_response = self.profile_node.get_followers(self.profile_node.id)
        if 'users' in follow_response:
            for user in follow_response['users']:
                if user['id_str'] in self.__graph.nodes:
                    self.__followers.append(self.__graph.nodes[user['id_str']])

    def get_following_nodes(self):
        follow_response = self.profile_node.get_following(self.profile_node.id)
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
        if not node.screen_name in self.__inverse_connections:
            return None
        parents = self.__inverse_connections[node.screen_name]
        if len(parents) == 0:
            return None

        return parents

    def pick_parent(self, feature_distances, id_list):
        feature_distances = np.cumsum(feature_distances)
        max_feature_length = feature_distances[-1]
        if max_feature_length == 0:
            feature_distances[0] = 1.0
        else:
            feature_distances = feature_distances / max_feature_length
        r_int = np.random.randint(low=0, high=len(id_list))
        return self.__graph.nodes[id_list[r_int]]


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

    def monte_carlo(self, root_node, samples=1, discount=0.8):
        if not root_node:
            raise ValueError('User not found !')
        self.feature_party = [root_node.party]
        for s in range(samples):
            chain_s = 0
            node = root_node

            search_users = {}
            search_users[root_node.screen_name] = str(chain_s)
            if np.linalg.norm(root_node.feature_vector) == 0:
                return root_node.feature_vector

            feature_vectors = [root_node.feature_vector]
            self.samples = np.concatenate([self.samples, np.asmatrix(root_node.feature_vector)], axis=0)
            node_list = [0, 0, 0, 0]
            chain_length = 0

            while node:
                node = self.get_parent_nodes(node)
                if node:
                    chain_s += 1
                    search_users[node.screen_name] = str(chain_s)

                if not node or node.screen_name == node_list[-2] or node.screen_name == node_list[-1] or node.screen_name == node_list[-3] or node.screen_name == node_list[-4]:
                    discounts = discount * np.ones(len(feature_vectors))
                    discounts = np.cumprod(discounts)
                    feature_vectors = feature_vectors * np.tile(discounts, (3, 1)).T
                    self.samples = np.concatenate([self.samples, feature_vectors], axis=0)
                    break

                feature_vectors.append(np.asarray(node.feature_vector))
                if chain_s < 8:
                    self.feature_party.append(node.party)
                node_list.append(node.screen_name)
                chain_length += 1

            if self.chain_target_node and self.chain_target_node.screen_name in search_users:
                self.print_chain(search_users)
                self.chain_users.append(search_users)

        RESULT = np.asarray(np.mean(self.samples, axis=0))[0]
        RESULT = RESULT / (0.000001 + np.linalg.norm(RESULT))
        print(RESULT)
        return RESULT

    def load_affiliation_list(self, path=None):
        if path is None:
            path = os.path.join(os.path.abspath(".."), 'data/affiliation_list.json')
        with open(path) as rfile:
            return json.load(rfile)

    def print_chain(self, users):
        for key, val in users.items():
            print(val, self.__graph.nodes[key].name, self.__graph.nodes[key].screen_name)
            if self.__graph.nodes[key].id == self.chain_target_node.id:
                print('-------------')
                break

    def show(self):
        if len(self.samples) == 0:
            return None
        fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)
        axs[0].hist(self.samples[:, 0], bins=200)
        axs[1].hist(self.samples[:, 1], bins=200)
        axs[2].hist(self.samples[:, 2], bins=200)
        plt.show()

