import boto3
import time
from datetime import datetime


class Dynamo:
    def __init__(self):
        self.dynamo = boto3.client('dynamodb')

    def save(self, viol_hash, violdttm, vendor_id):
        """Save info about this violation to Dynamo"""

        violdttm_parsed = datetime.strptime(violdttm, '%Y-%m-%dT%H:%M:%S.%f')
        violdttm_timestamp = time.mktime(violdttm_parsed.timetuple())

        self.dynamo.put_item(
            TableName='bff2',
            Item={
                'viol_hash': {
                    'S': viol_hash
                },
                'timestamp': {
                    'N': str(violdttm_timestamp)
                },
                'license': {
                    'S': str(vendor_id)
                }
            }
        )

    def query(self, viol_hash):
        """return true if this violation already exists in Dynamo"""

        resp = self.dynamo.get_item(
            TableName='bff2',
            Key={
                'viol_hash': {
                    'S': viol_hash
                }
            }
        )

        if 'Item' in resp and resp['Item']['viol_hash']['S'] == viol_hash:
            return True
        return False

    def count(self, license):
        """return number of known violations under this license number"""

        resp = self.dynamo.query(
            TableName='bff2',
            IndexName='license-index',
            KeyConditionExpression='license = :license',
            ExpressionAttributeValues={
                ':license': {
                    'S': license
                }
            }
        )

        return resp['Count']
