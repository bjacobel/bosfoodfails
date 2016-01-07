import boto3


class Dynamo:
    def __init__(self):
        self.dynamo = boto3.client('dynamodb')

    def save(self, text):
        """Save this <140 char sequence to Dynamo"""

        self.dynamo.put_item(
            TableName='BosFoodFails',
            Item={
                'text': {
                    'S': text
                }
            }
        )

    def query(self, text):
        """return true if this text already exists in Dynamo"""

        resp = self.dynamo.get_item(
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
