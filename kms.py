import boto3
import botocore.session
import os


class KMS:
    def __init__(self):
        self.dev = os.getcwd() == '/Users/bjacobel/code/personal/bosfoodfails'

        if self.dev:
            session = botocore.session.Session(profile='bjacobel')
            boto3.setup_default_session(botocore_session=session)

        kms = boto3.client('kms')
        cwd = os.getcwd()

        for secret in os.listdir('{}/secrets'.format(cwd)):
            with open('{}/secrets/{}'.format(cwd, secret), 'rb') as f:
                setattr(self, secret, kms.decrypt(
                    CiphertextBlob=f.read()
                )['Plaintext'])