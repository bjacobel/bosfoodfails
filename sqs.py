import boto3


class SQS:
    def __init__(self, config):
        self.config = config

        sqs = boto3.resource('sqs')
        self.queue = boto3.resource('sqs').get_queue_by_name(QueueName=config.SQSQueueName)

    def push(self, id, text, photo_url, lat, lon):
        attributes = {
            'text': {'StringValue': text, 'DataType': 'String'}
        }

        if lat and lon:
            attributes['lat'] = {'StringValue': str(lat), 'DataType': 'String'}
            attributes['lon'] = {'StringValue': str(lon), 'DataType': 'String'}

        if photo_url:
            attributes['photo_url'] = {'StringValue': photo_url, 'DataType': 'String'}

        self.queue.send_message(MessageBody=id, MessageAttributes=attributes)

    def pop(self):
        tweets = self.queue.receive_messages(
            MessageAttributeNames=['*']
        )

        if tweets:
            return tweets[0]
        return None
