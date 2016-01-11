# -*- coding: utf-8 -*-

from twython import Twython
from StringIO import StringIO

from kms import KMS


class Twitter:
    def __init__(self):
        config = KMS()

        self.twitter = Twython(
            config.TwitterConsumerKey,
            config.TwitterConsumerSecret,
            config.TwitterAccessToken,
            config.TwitterAccessTokenSecret
        )

        self.config = config

    def tweet(self, text, img, lat, lon):
        if self.config.dev:
            print(u'Tweeting to dev acct: {} @ ({}°, {}°)'.format(text, lat, lon))

        image_io = StringIO()
        img.save(image_io, 'PNG')
        image_io.seek(0)

        img_response = self.twitter.upload_media(media=image_io)

        self.twitter.update_status(
            status=text,
            lat=lat,
            long=lon,
            display_coordinates=True,
            media_ids=[img_response['media_id']]
        )
