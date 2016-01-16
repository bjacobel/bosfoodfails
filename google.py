import requests
from io import BytesIO
from urllib import urlencode
from random import choice

from kms import KMS


class GSV:
    def __init__(self, location_name, lat, lon, width=700, height=500):
        self.location_name = location_name
        self.width = width
        self.height = height
        self.lat = lat or 42.35989
        self.lon = lon or -71.058299
        self.config = KMS()

    def get_file(self, f=None):
        """Download the image, write it to an in-memory BytesIO object"""

        response = requests.get(self.get_url_new(), stream=True)

        if response.ok:
            if f is None:
                f = BytesIO(response.content)
        else:
            raise(response.reason)

        f.seek(0)
        return f

    def get_url_legacy(self):
        """Use the old "Street View Images API" which is super broken and old"""

        return (
            "https://maps.googleapis.com/maps/api/streetview"
            "?location={location}"
            "&size={width}x{height}"
        ).format(location=self.location_name, height=self.height, width=self.width)

    def place_search(self):
        """ Do a "Place Search" - https://developers.google.com/places/web-service/search"""

        query = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?" + urlencode({
            "keyword": self.location_name,
            "location": "{},{}".format(self.lat, self.lon),
            "key": self.config.GoogleMapsKey,
            "radius": 10000
        })

        place_search = requests.get(query)

        if not place_search.ok:
            raise Exception(place_search.reason)
        else:
            places = place_search.json()

            if places[u'status'] == u'ZERO_RESULTS':
                raise Exception("Couldn't be found on Google")
            else:
                return places[u'results'][0]

    def place_details(self, ref):
        """do a "Place details" query - https://developers.google.com/places/web-service/details"""

        query = "https://maps.googleapis.com/maps/api/place/details/json?" + urlencode({
            "key": self.config.GoogleMapsKey,
            "reference": ref
        })

        place_details = requests.get(query)

        if not place_details.ok:
            raise Exception(place_details.reason)
        else:
            return place_details.json()['result']

    def get_url_new(self):
        """Get the photo url using the newer "Places API" which is better but more complicated"""

        place = self.place_search()

        details = self.place_details(place[u'reference'])

        if 'photos' not in details:
            raise Exception("No photos found for this place")

        return "https://maps.googleapis.com/maps/api/place/photo?" + urlencode({
            "key": self.config.GoogleMapsKey,
            "photoreference": choice(details[u'photos'])['photo_reference'],
            "maxwidth": 880
        })
