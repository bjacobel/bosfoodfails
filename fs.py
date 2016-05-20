from foursquare import Foursquare
from random import choice
from io import BytesIO
import requests


class Fs:
    def __init__(self, config):
        self.config = config
        self.client = Foursquare(
            client_id=config.FoursquareClientId,
            client_secret=config.FoursquareClientSecret
        )

    def place_search(self, name, lat, lon):
        """returns foursquare place representation"""

        params = {
            'intent': 'browse',
            'query': name,
            'limit': 1
        }

        if not lat or not lon:
            params['near'] = "Boston, MA"
            params['radius'] = 10000
        else:
            params['ll'] = "{},{}".format(lat, lon)
            params['radius'] = 500

        venues = self.client.venues.search(params)['venues']

        if len(venues) > 0:
            return venues[0]
        else:
            return None

    def random_photo_url(self, place):
        photos = self.client.venues.photos(place['id'], params={
            'limit': 200
        })

        if len(photos['photos']['items']) > 0:
            photo = choice(photos['photos']['items'])

            return "{}width500{}".format(photo['prefix'], photo['suffix'])

        return None

    def photo_from_url(self, photo_url):
        resp = requests.get(photo_url, stream=True)

        if resp.ok:
            return BytesIO(resp.content)
        else:
            print("Couldn't save photo: " + resp.reason)
            return None
