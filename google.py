import requests
from io import BytesIO


class GSV:
    def __init__(self, location, width=700, height=500):
        self.location = location
        self.width = width
        self.height = height

    def get_file(self, f=None):
        """Download the image, write it to an in-memory BytesIO object"""

        response = requests.get(self.get_url(), stream=True)

        if response.ok:
            if f is None:
                f = BytesIO(response.content)
        else:
            raise(response.reason)

        f.seek(0)
        return f

    def get_url(self):
        return (
            "https://maps.googleapis.com/maps/api/streetview"
            "?location={location}"
            "&size={width}x{height}"
        ).format(location=self.location, height=self.height, width=self.width)
