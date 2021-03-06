import json
import re
import os
import copy
import api
import numpy as np
import sys


class NodeGenerator(api.twitterAPIWrapper):

    def __init__(self, CREDENTIALS):
        super().__init__(CREDENTIALS)
        self.user_object = None
        self.__scname = None
        self.__id = None
        self.__description = None
        self.__profile_pic = None
        self.__location = None
        self.__name = None
        self.__followers = None
        self.__party = None
        self.__feature_vector = None

    def new(self, twitter_id, party=None):
        if isinstance(twitter_id, dict):
            self.user_object = twitter_id

        elif isinstance(twitter_id, str):
            if twitter_id[0] == '@':
                self.user_object = self.get_user_by_screen_name(twitter_id)
            else:
                self.user_object = self.get_user_by_id(twitter_id)
        else:
            return False

        self.__scname = self.get_field('screen_name')
        self.__id = self.get_field('id')
        self.__description = self.get_field('description')
        self.__profile_pic = self.get_field('profile_image_url')
        self.__location = self.get_field('location')
        self.__name = self.get_field('name')
        self.__followers = self.get_field('followers_count')
        self.__party = self.get_affiliation()

        if party:
            self.__party = party

        self.__feature_vector = [0, 0, 0]
        if self.__party:
            self.__feature_vector = self.get_feature_map(self.__party)

        del self.user_object
        return copy.deepcopy(self)

    def get_feature_map(self, party, path=None):
        if path is None:
            path = os.path.join(os.path.abspath("../"), 'data/affiliation_list.json')

        with open(path) as rfile:
            party_values = json.load(rfile)
            if party in party_values:
                features = party_values[party][0]
                prior_mean = [features['eco'], features['img'], features['cli']]
            else:
                prior_mean = [0, 0, 0]
            return prior_mean

    def get_connections(self, screen_name):
        liked_tweets = self.get_likes(screen_name)
        connections = []
        for tweet in liked_tweets:
            if 'id' in tweet:
                if 'lang' in tweet and tweet['lang'] == 'da':
                    connections.append(tweet['user'])
        return connections

    def get_field(self, field):
        if field in self.user_object:
            return self.user_object[field]
        if 'entities' in self.user_object and field in self.user_object['entities']:
            return self.user_object['entities'][field]
        return None

    def load_affiliation_list(self, path=None):
        if path is None:
            path = os.path.join(os.path.abspath("../"), 'data/affiliation_list.json')
        with open(path) as rfile:
            return json.load(rfile)

    def format_word(self, keyword):
        keyword = re.sub(r'\W+', '', keyword)
        keyword = re.sub(' ', '', keyword).lower()
        return keyword

    def get_affiliation(self):
        self.__party = None
        if not isinstance(self.__description, str):
            return False

        word_list = self.__description.split(' ')
        affiliation_list = self.load_affiliation_list()
        for key, keywords in affiliation_list.items():
            for keyword in keywords:
                if not isinstance(keyword, str):
                    continue
                keyword = self.format_word(keyword)
                for idx, word in enumerate(word_list):
                    word0 = self.format_word(word)

                    word1 = ''
                    if idx+1 < len(word_list):
                        word1 = self.format_word(word_list[idx+1])

                    if keyword == word0 or \
                            keyword == self.format_word(self.__name) or \
                            keyword == self.format_word(self.__scname) or \
                            keyword == (word0+word1):
                        return key
        return False

    def set_feature_vector(self, new_feature_vector):
        self.__feature_vector = new_feature_vector

    def set_party(self, new_party):
        self.__party = new_party

    @property
    def id(self):
        return str(self.__id)

    @property
    def profile_pic(self):
        return str(self.__profile_pic)

    @property
    def location(self):
        return str(self.__location)

    @property
    def description(self):
        return str(self.__description)

    @property
    def followers(self):
        if self.__followers:
            return int(self.__followers)
        return 0

    @property
    def name(self):
        return self.__name

    @property
    def party(self):
        return self.__party

    @property
    def feature_vector(self):
        return self.__feature_vector

    @property
    def screen_name(self):
        return self.__scname






