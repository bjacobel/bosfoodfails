#!/bin/bash

rm bff-tweeter.zip
rm bff-queuer.zip

zip bff-tweeter.zip ./*.py
zip -r bff-tweeter.zip ./secrets

zip bff-queuer.zip ./*.py
zip -r bff-queuer.zip ./secrets

pushd ~/.virtualenvs/bosfoodfails/lib/python2.7/site-packages
zip -r ~/code/personal/bosfoodfails/bff-tweeter.zip ./*
zip -r ~/code/personal/bosfoodfails/bff-queuer.zip ./*
popd

aws lambda update-function-code \
  --function-name BosFoodFails \
  --zip-file fileb://~/code/personal/bosfoodfails/bff-tweeter.zip

aws lambda update-function-code \
  --function-name BosFoodFailsQueuer \
  --zip-file fileb://~/code/personal/bosfoodfails/bff-queuer.zip
