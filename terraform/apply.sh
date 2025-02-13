#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' ../.env | xargs)

# Run Terraform commands
terraform init
terraform fmt
terraform validate
terraform apply \
  -var "AWS_ACCESS_KEY=$AWS_ACCESS_KEY" \
  -var "AWS_SECRET_KEY=$AWS_SECRET_KEY" \
  -var "LEDAA_WEB_SCRAPPER_ARN=$LEDAA_WEB_SCRAPPER_ARN" \
  -var "LEDAA_TEXT_SPLITTER_LAMBDA_LAYER_ARN=$LEDAA_TEXT_SPLITTER_LAMBDA_LAYER_ARN"