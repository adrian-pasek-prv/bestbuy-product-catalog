#!/bin/bash

# Extract public key for Snowflake without header and footer
data_loader_snowflake_user_pub_key=$(awk '!/-----BEGIN PUBLIC KEY-----/ && !/-----END PUBLIC KEY-----/' ../config/data_loader_snowflake_user.pub)
# Use jq to format the data as JSON - it is mandatory to return a valid JSON
jq -n \
  --arg pub_key "$data_loader_snowflake_user_pub_key" \
  '{"data_loader_snowflake_user_pub_key":$pub_key}'