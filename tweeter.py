from twitter import Twitter
from kms import KMS
from sqs import SQS


def handler(event, context):
    config = KMS()
    sqs = SQS(config)
    twitter = Twitter(config)
    tweet = sqs.pop()

    if tweet:
        print('Got tweet {} from SQS, tweeting it'.format(tweet.body))

        text = tweet.message_attributes.get('text')
        photo_url = tweet.message_attributes.get('photo_url')
        lat = tweet.message_attributes.get('lat')
        lon = tweet.message_attributes.get('lon')

        twitter.tweet(
            text.get('StringValue') if text else None,
            photo_url.get('StringValue') if photo_url else None,
            lat.get('StringValue') if lat else None,
            lon.get('StringValue') if lon else None
        )

        tweet.delete()

if __name__ == "__main__":
    handler(None, None)
