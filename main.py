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
    return u'{bn} ({address}, {city}) failed {reason} check on {date}.'.format(
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

    scale_factor = 2
    margin = 20 * scale_factor
    base_width = 440 * scale_factor
    base_height = 1000 * scale_factor
    font_size = 16 * scale_factor
    spacing = int(font_size / 2.2)

    img = Image.new('RGBA', (base_width, base_height), 'white')
    helvneu = ImageFont.truetype(font='./HelveticaNeue-Regular.ttf', size=font_size)

    singleline_comments = viol['comments']
    comments = ''
    px_across = margin
    for word in singleline_comments.split(' '):
        px_across += ImageDraw.Draw(img).textsize(word + ' ', helvneu)[0]

        if px_across > (base_width - 2 * margin):
            px_across = margin
            comments = comments + '\n'

        comments = comments + ' ' + word

    ImageDraw.Draw(img).multiline_text(
        (margin, margin),
        comments,
        fill='black',
        font=helvneu,
        spacing=spacing,
        align='left'
    )

    (text_w, text_h) = ImageDraw.Draw(img).multiline_textsize(
        text=comments,
        font=helvneu,
        spacing=spacing
    )

    img = img.crop((0, 0, base_width, text_h + 2 * margin))

    if scale_factor > 1:
        img = img.resize(
            (base_width / scale_factor, img.height / scale_factor),
            Image.BICUBIC
        )

    return img


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
    yesterday_begin = today_begin - timedelta(days=2)

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

            db.save(viol_hash, viol['violdttm'], viol['licenseno'])

            break
        else:
            print('Violation already known to Dynamo')


if __name__ == "__main__":
    handler(None, None)
