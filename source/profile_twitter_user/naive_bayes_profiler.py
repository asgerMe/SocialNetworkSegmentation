import re
import numpy as np

class NaiveBayesClassifier:
    def __init__(self, name, graph, nodegen):
        self.graph = graph
        self.profile_node = None
        self.vocab, self.n_tweets = self.get_vocab()

        self.twitter_node = nodegen.new(name)
        self.text = self.twitter_node.description
        self.recent_tweets = self.twitter_node.get_tweets(twitter_id=self.twitter_node.id)
        #tweettext = self.recent_tweets
        #for unit in tweettext:
        #    self.text += unit['text'] + ' '

    def __call__(self, *args, **kwargs):
        if self.text == '':
            raise ConnectionError('Twitter api is not responsive. No text was retrieved')
        result = {}
        word_match = 0
        for party, vocab in self.vocab.items():
            p_cl = 0.0
            word_list = {}
            for word in self.text.split(' '):
                word = self.standardize_word(word)
                if not word or word in word_list:
                    continue
                word_list[word] = True
                pi = 1.0 / 1200
                if word in vocab:
                    print(word, party)
                    word_match += 1
                    pi = vocab[word]
                p_cl += np.log(pi)

            result[party] = p_cl
        if word_match > 0:
            return sorted(result, key=result.get)[-3:]
        else:
            return []

    def get_vocab(self):
        vocab = {}
        n_tweets_by_party = {}
        for node in self.graph.nodes.values():
            if not node.party:
                continue
            try:
                words_per_tweet = {}
                for word in node.description.split(' '):
                    word = self.standardize_word(word)
                    if not word or word in words_per_tweet:
                        continue
                    words_per_tweet[word] = True
                    if node.party in vocab:
                        vocab[node.party].append(word)
                        n_tweets_by_party[node.party] += 1
                    else:
                        vocab[node.party] = [word]
                        n_tweets_by_party[node.party] = 1
            except OSError:
                pass

        p_wc_ = {}
        for party in vocab:
            p_wc_[party] = {}
            word_occurences = list(np.unique(vocab[party], return_counts=True))
            word_occurences[1] = word_occurences[1] / n_tweets_by_party[party]

            for word, word_prob in zip(word_occurences[0], word_occurences[1]):
                p_wc_[party][word] = word_prob
        return p_wc_, n_tweets_by_party

    def standardize_word(self, word):
        if len(word) <= 5:
            return False
        if word[-1:] == 's' or word[-1:] == 'e':
            word = word[:-1]
        if word[-2:] == 'er' or word[-2:] == 'en' or word[-2:] == 'de':
            word = word[:-2]
        if word[-3:] == 'ere':
            word = word[:-3]

        word = self.format_word(word)
        return word

    def format_word(self, keyword):
        keyword = re.sub(r'\W+', '', keyword)
        keyword = re.sub(' ', '', keyword).lower()
        return keyword
