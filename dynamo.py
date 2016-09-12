import boto3

class Dynamo:
    def __init__(self, config):
        self.config = config
        self.dynamo = boto3.client('dynamodb')

    def save(self, viol_id, license_id):
        """Save info about this violation to Dynamo"""

        self.dynamo.put_item(
            TableName=self.config.DynamoTableName,
            Item={
                'id': {
                    'S': viol_id
                },
                'license': {
                    'S': license_id
                }
            }
        )

    def query(self, viol_id):
        """return true if this violation already exists in Dynamo"""

        resp = self.dynamo.get_item(
            TableName=self.config.DynamoTableName,
            Key={
                'id': {
                    'S': viol_id
                }
            }
        )

        if 'Item' in resp and resp['Item']['id']['S'] == viol_id:
            return True
        return False

    def count(self, license_id):
        """return number of known violations under this license number"""

        resp = self.dynamo.query(
            TableName=self.config.DynamoTableName,
            IndexName='license-index',
            KeyConditionExpression='license = :license',
            ExpressionAttributeValues={
                ':license': {
                    'S': license_id
                }
            }
        )

        return resp['Count']
