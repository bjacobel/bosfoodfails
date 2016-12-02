#!/bin/bash

dir="$(pwd)"

zip -ru bff.zip ./*.py
zip -ru bff.zip ./secrets -x secrets/dev/*

source ~/.virtualenvs/bosfoodfails/bin/activate
pip install -r requirements.txt
deactivate

pushd ~/.virtualenvs/bosfoodfails/lib/python2.7/site-packages
zip -ru $dir/bff.zip ./*
popd

aws lambda update-function-code \
  --profile=bjacobel \
  --function-name BosFoodFails \
  --zip-file fileb://$dir/bff.zip
