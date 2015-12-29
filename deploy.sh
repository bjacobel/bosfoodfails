#!/bin/bash

zip bff.zip bff.py
zip -r bff.zip ./secrets
pushd ~/.virtualenvs/bosfoodfails/lib/python2.7/site-packages
zip -r ~/code/personal/bosfoodfails/bff.zip ./*
popd

aws --profile bjacobel lambda update-function-code \
  --function-name BosFoodFails \
  --zip-file fileb://~/code/personal/bosfoodfails/bff.zip
