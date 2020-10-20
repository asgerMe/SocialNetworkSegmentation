import requests
import numpy as np


class twitterAPIWrapper:

    def __init__(self, key):
        self.CREDENTIALS = key

    @classmethod
    def get_ids(cls, request_func):
        res = []
        for response in request_func:
            if 'id' in response:
                res.append(response['id'])
        return list(np.unique(res))

    def get_user_by_screen_name(self, screen_name='twitterdev'):
        base_url = 'https://api.twitter.com/1.1/users/show.json?screen_name={}'.format(screen_name)
        followers = requests.get(base_url, headers={"content-type": "text", 'authorization': 'Bearer {}'.format(self.CREDENTIALS['token'])})
        return followers.json()

    def get_user_by_id(self, twitter_id=''):
        if not isinstance(twitter_id, str):
            twitter_id = str(twitter_id)

        base_url = 'https://api.twitter.com/1.1/users/show.json?id={}'.format(twitter_id)
        followers = requests.get(base_url, headers={"content-type": "text",
                                                    'authorization': 'Bearer {}'.format(self.CREDENTIALS['token'])})
        return followers.json()

    def get_followers(self, twitter_id='twitterdev'):
        base_url = 'https://api.twitter.com/1.1/followers/list.json?id={}'.format(twitter_id)
        followers = requests.get(base_url, headers={"content-type":"text", 'authorization': 'Bearer {}'.format(self.CREDENTIALS['token'])})

        return followers.json()

    def get_following(self, twitter_id='twitterdev'):
        base_url = 'https://api.twitter.com/1.1/friends/list.json?twitter_id={}'.format(twitter_id)
        followers = requests.get(base_url, headers={"content-type":"text", 'authorization': 'Bearer {}'.format(self.CREDENTIALS['token'])})
        return followers.json()

    def get_likes(self, twitter_id='twitterdev'):
        base_url = 'https://api.twitter.com/1.1/favorites/list.json?id={}'.format(twitter_id)
        followers = requests.get(base_url, headers={"content-type": "text", 'authorization': 'Bearer {}'.format(self.CREDENTIALS['token'])})
        print('Call API')
        if 'errors' in followers.json():
            print(followers.json()['errors'])
            print('..................')
        return followers.json()

    def get_tweets(self, twitter_id='twitterdev'):
        base_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?id={}'.format(twitter_id)
        followers = requests.get(base_url, headers={"content-type": "text", 'authorization': 'Bearer {}'.format(self.CREDENTIALS['token'])})
        return followers.json()



