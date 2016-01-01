# -*- coding: utf-8 -*-

from addict import Dict
from datetime import datetime, timedelta
from sodapy import Socrata
import boto3
import botocore.session
import os
import re
import tweepy

config = Dict()


def get_config():
    if os.getcwd() == '/Users/bjacobel/code/personal/bosfoodfails':  # Only do this in dev
        session = botocore.session.get_session()
        session.profile = 'bjacobel'
        boto3.setup_default_session(botocore_session=session)

    kms = boto3.client('kms')

    for secret in os.listdir('./secrets'):
        with open('./secrets/' + secret, 'rb') as f:
            config[secret] = kms.decrypt(
                CiphertextBlob=f.read()
            )['Plaintext']


def save_dynamo(text):
    """Save this <140 char sequence to Dynamo"""
    dynamo = boto3.client('dynamodb')

    dynamo.put_item(
        TableName='BosFoodFails',
        Item={
            'text': {
                'S': text
            }
        }
    )


def query_dynamo(text):
    """return true if this text already exists in Dynamo"""
    dynamo = boto3.client('dynamodb')

    resp = dynamo.get_item(
        TableName='BosFoodFails',
        Key={
            'text': {
                'S': text
            }
        }
    )

    if 'Item' in resp and resp['Item']['text']['S'] == text:
        return True
    return False


def tweet(text):
    auth = tweepy.OAuthHandler(config.TwitterConsumerKey, config.TwitterConsumerSecret)
    auth.set_access_token(config.TwitterAccessToken, config.TwitterAccessTokenSecret)

    api = tweepy.API(auth)

    api.update_status(text)


def correct_case(str):
    return str.lower().title()


def correct_spacing(str):
    return re.sub(' +', ' ', str)


def format_msg(viol):
    text = u"{bn} ({address}, {city}) failed check on {date}. {desc}".format(
        bn=correct_case(viol[u'businessname']),
        address=correct_spacing(correct_case(viol[u'address'])),
        city=correct_case(viol[u'city']),
        date=datetime.strptime(viol[u'violdttm'], '%Y-%m-%dT%H:%M:%S.%f').strftime('%m/%d'),
        desc=correct_spacing(viol[u'violdesc']),
    )

    if u'comments' in viol:
        text += u": {}".format(viol[u'comments'])

    if len(text) > 140:
        text = text[:139] + u'…'

    return text


def lambda_handler(event, context):
    get_config()

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

    print("Got {} violations".format(len(viols)))

    for viol in viols:
        text = format_msg(viol)

        if not query_dynamo(text):
            print('Violation not found in Dynamo, saving it there and tweeting it')
            save_dynamo(text)
            tweet(text)
            break
        else:
            print("Violation already known to Dynamo")

if __name__ == '__main__':
    lambda_handler(None, None)
