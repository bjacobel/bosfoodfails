# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from sodapy import Socrata
from titlecase import titlecase
from random import shuffle
import re

from dynamo import Dynamo
from kms import KMS
from twitter import Twitter
from fs import Fs  # sorry this was bad but the foursquare client library I'm using already used the full name


def correct_casing(str):
    str = titlecase(str)
    str = re.sub(r'\bST\b', 'St.', str)
    str = re.sub(r'\bAV\b', 'Av.', str)
    str = re.sub(r'\bDR\b', 'Dr.', str)
    str = re.sub(r'\bPK\b', 'Pk.', str)
    str = re.sub(r'\bLA\b', 'La.', str)
    return str


def correct_spacing(str):
    return re.sub(' +', ' ', str)


def clean(str):
    return correct_casing(
        correct_spacing(
            str
        )
    )


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def format_url(viol):
    return "https://bosfoodfails.bjacobel.com/#/{}".format(viol[':id'])


def format_msg(viol, count, reason_url):
    return u'{bn} ({address}, {city}) failed check for the {ord} time. Details: {url}'.format(
        bn = clean(viol[u'businessname']),
        address = clean(viol[u'address']),
        city = clean(viol[u'city']),
        ord = ordinal(count + 1),
        url = reason_url
    )


def extract_geo(viol):
    lat = None
    lon = None

    if u'location' in viol:
        # This appears to be in the API in two different structures?
        if 'longitude' in viol['location'] and 'latitude' in viol['location']:
            lat = viol[u'location'][u'latitude']
            lon = viol[u'location'][u'longitude']
        elif 'coordinates' in viol['location']:
            lat = viol['location']['coordinates'][1]
            lon = viol['location']['coordinates'][0]

    return lat, lon


def get_viols(client):
    now = datetime.now()
    today_begin = now - timedelta(
        microseconds=now.microsecond,
        seconds=now.second,
        minutes=now.minute,
        hours=now.hour
    )
    yesterday_begin = today_begin - timedelta(days=3)

    where_clause = 'violstatus = \'Fail\' AND violdttm between \'{}\' and \'{}\''.format(
        yesterday_begin.isoformat(),
        today_begin.isoformat()
    )

    viols = client.get('427a-3cn5', where=where_clause, select=":*, *")

    print('Got {} violations'.format(len(viols)))

    shuffle(viols)

    return viols


def handler(event, context):
    config = KMS()
    db = Dynamo(config)
    twitter = Twitter(config)
    foursquare = Fs(config)

    client = Socrata(
        domain='data.cityofboston.gov',
        app_token=config.SocrataAppToken,
        username='bjacobel@gmail.com',
        password=config.SocrataPassword
    )

    viols = get_viols(client)

    client.close()

    for viol in viols:

        if not db.query(viol[':id']):
            print('Violation not found in Dynamo, saving it there and tweeting it')

            count = db.count(viol['licenseno'])
            url = format_url(viol)
            text = format_msg(viol, count, url)
            (lat, lon) = extract_geo(viol)

            place = foursquare.place_search(
                name=viol['businessname'],
                lat=lat,
                lon=lon
            )

            photo = None

            if place:
                photo = foursquare.random_photo(place)

            twitter.tweet(text, photo, lat, lon)

            db.save(viol[':id'], viol['licenseno'])

            break
        else:
            print('Violation already known to Dynamo')


if __name__ == "__main__":
    handler(None, None)
