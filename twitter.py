import tweepy
from kms import KMS


class Twitter:
    def __init__(self):
        config = KMS()

        auth = tweepy.OAuthHandler(config.TwitterConsumerKey, config.TwitterConsumerSecret)
        auth.set_access_token(config.TwitterAccessToken, config.TwitterAccessTokenSecret)

        self.api = tweepy.API(auth)
        self.config = config

    def tweet(self, text):
        if self.config.dev:
            print(u'Would tweet: {}'.format(text))
        else:
            self.api.update_status(text)
