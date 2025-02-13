#!/bin/bash

# Create a directory for the python layer
mkdir -p layers/python

# cd into python directory
cd layers/python

# Install the required packages in the python directory for arm64
pip3 install --only-binary=:all: -r ../../requirements.txt -t .

# cd back to the parent directory
cd ..

# remove older zip file
rm -f ../terraform/packages/ledaa_text_splitter_lambda_layer.zip

# Zip the contents of the python directory
zip -r ../terraform/packages/ledaa_text_splitter_lambda_layer.zip .

# Remove the layers/python directory
cd ..
rm -rf layers
