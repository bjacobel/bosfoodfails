# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from sodapy import Socrata
from titlecase import titlecase
from pprint import pformat
from hashlib import md5
from PIL import Image, ImageDraw, ImageFont
import re
import json

from dynamo import Dynamo
from kms import KMS
from twitter import Twitter


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


def format_msg(viol):
    return u'{bn} ({address}, {city}) failed {reason} check on {date}. Full comments:'.format(
        bn = clean(viol[u'businessname']),
        address = clean(viol[u'address']),
        city = clean(viol[u'city']),
        date = datetime.strptime(viol[u'violdttm'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%m/%d'),
        reason = clean(viol[u'violdesc']),
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
            lat = viol['location']['coordinates'][0]
            lon = viol['location']['coordinates'][1]

    return lat, lon


def create_img(viol):
    if 'comments' not in viol:
        return None

    img = Image.new('RGBA', (440, 220), 'white')
    helvneu = ImageFont.truetype(font='./HelveticaNeue-Medium.ttf', size=16)

    singleline_comments = viol['comments']
    comments = ''
    px_across = 20
    for word in singleline_comments.split(' '):
        px_across += ImageDraw.Draw(img).textsize(word + ' ', helvneu)[0]

        if px_across > 400:
            px_across = 20
            comments = comments + '\n'

        comments = comments + ' ' + word

    ImageDraw.Draw(img).multiline_text(
        (20, 20),
        comments,
        fill='black',
        font=helvneu,
        spacing=6,
        align='left'
    )

    (imgw, imgh) = ImageDraw.Draw(img).multiline_textsize(
        text=comments,
        font=helvneu,
        spacing=6
    )

    return img.crop((0, 0, imgw + 40, imgh + 40))


def hashd(viol):
    return md5(pformat(viol)).hexdigest()


def handler(event, context):
    config = KMS()
    db = Dynamo()
    twitter = Twitter()

    client = Socrata(
        domain='data.cityofboston.gov',
        app_token=config.SocrataAppToken,
        username='bjacobel@gmail.com',
        password=config.SocrataPassword
    )

    now = datetime.now()
    today_begin = now - timedelta(
        microseconds=now.microsecond,
        seconds=now.second,
        minutes=now.minute,
        hours=now.hour
    )
    yesterday_begin = today_begin - timedelta(days=1)

    where_clause = 'violstatus = \'Fail\' AND violdttm between \'{}\' and \'{}\''.format(
        yesterday_begin.isoformat(),
        today_begin.isoformat()
    )

    viols = client.get('427a-3cn5', where=where_clause)

    client.close()

    print('Got {} violations'.format(len(viols)))

    for viol in viols:
        viol_hash = hashd(viol)

        if not db.query(viol_hash):
            print('Violation not found in Dynamo, saving it there and tweeting it')

            text = format_msg(viol)
            img = create_img(viol)
            (lat, lon) = extract_geo(viol)

            twitter.tweet(text, img, lat, lon)

            db.save(viol_hash)

            break
        else:
            print('Violation already known to Dynamo')


if __name__ == "__main__":
    handler(None, None)
