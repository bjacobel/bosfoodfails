# -*- coding: utf-8 -*-

from twython import Twython
from twython.exceptions import TwythonError
from fs import Fs

class Twitter:
    def __init__(self, config):
        self.config = config

        self.twitter = Twython(
            config.TwitterConsumerKey,
            config.TwitterConsumerSecret,
            config.TwitterAccessToken,
            config.TwitterAccessTokenSecret
        )

        self.foursquare = Fs(config)

    def tweet(self, text, img, lat, lon):
        if self.config.dev:
            print(u'Tweeting to dev acct: {} @ ({}°, {}°)'.format(text, lat, lon))
            if img:
                print("Will have image")

        try:
            if img:
                img_obj = self.foursquare.photo_from_url(img)
                img_response = self.twitter.upload_media(media=img_obj)

                self.twitter.update_status(
                    status=text,
                    lat=lat,
                    long=lon,
                    display_coordinates=True,
                    media_ids=[img_response['media_id']]
                )
            else:
                self.twitter.update_status(
                    status=text,
                    lat=lat,
                    long=lon,
                    display_coordinates=True
                )
        except TwythonError as e:
            print(e)
