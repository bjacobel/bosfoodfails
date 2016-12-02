#!/bin/bash

rm bff.zip
zip -ru bff.zip ./*.py
zip -ru bff.zip ./secrets -x secrets/dev/*

pushd ~/.virtualenvs/bosfoodfails/lib/python2.7/site-packages
zip -ru $(pwd)/bff.zip ./*
popd

aws lambda update-function-code \
  --profile=bjacobel \
  --function-name BosFoodFails \
  --zip-file fileb://$(pwd)/bff.zip
