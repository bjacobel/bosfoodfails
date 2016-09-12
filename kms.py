import boto3
import os

class KMS:
    def __init__(self):
        self.dev = os.getcwd() == '/Users/bjacobel/code/bosfoodfails'

        kms = boto3.client('kms')
        cwd = os.getcwd()

        for secret in os.listdir('{}/secrets'.format(cwd)):
            if secret == "dev":
                continue

            with open('{}/secrets/{}'.format(cwd, secret), 'rb') as f:
                setattr(self, secret, kms.decrypt(
                    CiphertextBlob=f.read()
                )['Plaintext'])

        # overwrite any real credentials with things you find in /secrets/dev
        # these are kept out of the lambda build
        for secret in os.listdir('{}/secrets/dev'.format(cwd)):
            with open('{}/secrets/dev/{}'.format(cwd, secret), 'rb') as f:
                setattr(self, secret, kms.decrypt(
                    CiphertextBlob=f.read()
                )['Plaintext'])

        self.DynamoTableName = 'bosfoodfails'

        if self.dev:
            self.DynamoTableName = 'bosfoodfails-dev'
