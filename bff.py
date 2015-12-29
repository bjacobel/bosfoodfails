# -*- coding: utf-8 -*-

from addict import Dict
from sodapy import Socrata
import boto3
import botocore.session
from datetime import datetime
import os
import re


def get_config(context):
    if not context:  # Running in development
        session = botocore.session.get_session()
        session.profile = 'bjacobel'
        boto3.setup_default_session(botocore_session=session)

    kms = boto3.client('kms')

    config = Dict()

    for secret in os.listdir('./secrets'):
        with open('./secrets/' + secret, 'rb') as f:
            config[secret] = kms.decrypt(
                CiphertextBlob=f.read()
            )['Plaintext']

    return config


def correct_case(str):
    return str.lower().title()


def correct_spacing(str):
    return re.sub(' +', ' ', str)


def handle_violation(viol):
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

    print(text)


def lambda_handler(event, context):
    config = get_config(context)

    client = Socrata(
        domain='data.cityofboston.gov',
        app_token=config.SocrataAppToken,
        username='bjacobel@gmail.com',
        password=config.SocrataPassword
    )

    query = 'violstatus = \'Fail\''

    viols = client.get('427a-3cn5', where=query, order='violdttm DESC', limit=100)

    client.close()

    for viol in viols:
        handle_violation(viol)

if __name__ == '__main__':
    lambda_handler(None, None)
