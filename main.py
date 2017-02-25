# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from ckanapi import RemoteCKAN
from titlecase import titlecase
from random import shuffle
import re

from dynamo import Dynamo
from kms import KMS
from twitter import Twitter
from fs import Fs  # sorry this was bad but the foursquare client library I'm using already used the full name


def correct_casing(string):
    string = titlecase(string)
    string = re.sub(r'\bST\b', 'St.', string)
    string = re.sub(r'\bAV\b', 'Av.', string)
    string = re.sub(r'\bDR\b', 'Dr.', string)
    string = re.sub(r'\bPK\b', 'Pk.', string)
    string = re.sub(r'\bLA\b', 'La.', string)
    return string


def correct_spacing(string):
    return re.sub(' +', ' ', string)


def clean(string):
    return correct_casing(
        correct_spacing(
            string
        )
    )


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def format_url(viol):
    return "https://bosfoodfails.bjacobel.com/#/{}".format(viol['_id'])


def format_msg(viol, count, reason_url):
    return u'{bn} ({address}, {city}) failed check for the {ord} time. Details: {url}'.format(
        bn=clean(viol[u'businessName']),
        address=clean(viol[u'Address']),
        city=clean(viol[u'CITY']),
        ord=ordinal(count + 1),
        url=reason_url
    )


def extract_geo(viol):
    lat = None
    lon = None

    if u'Location' in viol and viol['Location']:
        print(viol['Location'])
        match = re.match('\((\d+\.\d+), (-\d+\.\d+)\)', viol['Location'])
        lat = float(match.group(1))
        lon = float(match.group(2))

    return lat, lon


def get_viols(client):
    now = datetime.now()
    today_begin = now - timedelta(
        microseconds=now.microsecond,
        seconds=now.second,
        minutes=now.minute,
        hours=now.hour
    )
    yesterday_begin = today_begin - timedelta(days=7)

    viols = client.action.datastore_search_sql(
        sql=(
            'SELECT * FROM "4582bec6-2b4f-4f9e-bc55-cbaa73117f4c" WHERE '
            '"ViolStatus" = \'Fail\' AND'
            '"VIOLDTTM" between \'{}\' and \'{}\' AND '
            '"ViolLevel" in(\'**\', \'***"\')'
        ).format(
            yesterday_begin.isoformat(),
            today_begin.isoformat()
        )
    )['records']

    print('Got {} violations'.format(len(viols)))

    shuffle(viols)

    return viols


def handler(event, context):
    config = KMS()
    db = Dynamo(config)
    foursquare = Fs(config)
    twitter = Twitter(config)

    client = RemoteCKAN('https://data.boston.gov')

    viols = get_viols(client)

    client.close()

    for viol in viols:

        if not db.query(viol['_id']):

            count = db.count(viol['LICENSENO'])
            url = format_url(viol)
            text = format_msg(viol, count, url)
            (lat, lon) = extract_geo(viol)

            place = foursquare.place_search(
                name=viol['businessName'],
                lat=lat,
                lon=lon
            )

            photo_url = None

            if place:
                photo_url = foursquare.random_photo_url(place)

            twitter.tweet(text, photo_url, lat, lon)

            db.save(viol['_id'], viol['LICENSENO'])

            break
        else:
            print('Violation already known to Dynamo')


if __name__ == "__main__":
    handler(None, None)
