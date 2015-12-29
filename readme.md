###bosfoodfails

Get recent "food establishment" inspection violations and tweet them to [@bosfoodfails](https://twitter.com/bosfoodfails).

Uses AWS Lambda, AWS KMS and the Socrata API ([data.cityofboston.gov](https://data.cityofboston.gov)'s Open Data vendor).


####Deploy to Lambda:

        pip install kappa
        kappa config.yml create
        kappa config.yml update_code

####KMS secret management:
Encrypt:

        aws --profile bjacobel kms encrypt --key-id <key> --plaintext "<secretValue>" --query CiphertextBlob --output text | base64 --decode > ./secrets/<secretKey>


Decrypt:

    with open('./secrets/<secretKey>', 'rb') as f:
        print(kms.decrypt(
            CiphertextBlob=f.read()
            )['Plaintext'])
