import boto3


class Dynamo:
    def __init__(self):
        self.dynamo = boto3.client('dynamodb')

    def save(self, viol_hash):
        """Save the hash of this violation to Dynamo"""

        self.dynamo.put_item(
            TableName='bff2',
            Item={
                'text': {
                    'S': viol_hash
                }
            }
        )

    def query(self, viol_hash):
        """return true if this violation already exists in Dynamo"""

        resp = self.dynamo.get_item(
            TableName='bff2',
            Key={
                'text': {
                    'S': viol_hash
                }
            }
        )

        if 'Item' in resp and resp['viol_hash']['text']['S'] == viol_hash:
            return True
        return False
