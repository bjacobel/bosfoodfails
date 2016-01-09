import boto3


class Dynamo:
    def __init__(self):
        self.dynamo = boto3.client('dynamodb')

    def save(self, viol_hash):
        """Save the hash of this violation to Dynamo"""

        self.dynamo.put_item(
            TableName='bff2',
            Item={
                'viol_hash': {
                    'S': viol_hash
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
