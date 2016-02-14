import boto3
import botocore.session
import os


class KMS:
    def __init__(self):
        self.dev = os.getcwd() == '/Users/bjacobel/code/personal/bosfoodfails'

        kms = boto3.client('kms')
        cwd = os.getcwd()

        for secret in os.listdir('{}/secrets'.format(cwd)):
            if secret == "dev":
                continue

            with open('{}/secrets/{}'.format(cwd, secret), 'rb') as f:
                setattr(self, secret, kms.decrypt(
                    CiphertextBlob=f.read()
                )['Plaintext'])

        self.DynamoTableName = 'bosfoodfails'

        # not encrypted, .gitignored
        if self.dev:
            with open(cwd + '/secrets/dev/TwitterAccessToken', 'r') as f:
                self.TwitterAccessToken = f.read().rstrip()
            with open(cwd + '/secrets/dev/TwitterAccessTokenSecret', 'r') as f:
                self.TwitterAccessTokenSecret = f.read().rstrip()
            with open(cwd + '/secrets/dev/TwitterConsumerKey', 'r') as f:
                self.TwitterConsumerKey = f.read().rstrip()
            with open(cwd + '/secrets/dev/TwitterConsumerSecret', 'r') as f:
                self.TwitterConsumerSecret = f.read().rstrip()

            self.DynamoTableName = 'bosfoodfails-dev'
