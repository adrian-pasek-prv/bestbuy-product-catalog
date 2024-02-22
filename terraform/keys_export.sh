#!/bin/bash

# Extract public key for Snowflake without header and footer and remove new line '\n' due to issues with parsing a JSON
data_loader_snowflake_user_pub_key=$(awk '!/-----BEGIN PUBLIC KEY-----/ && !/-----END PUBLIC KEY-----/' ~/.ssh/data_loader_snowflake_user.pub)
# Extract private key for Airflow, header and footer included
data_loader_snowflake_user_priv_key=$(cat ~/.ssh/data_loader_snowflake_user.p8)

# Use jq to format the data as JSON
jq -n \
  --arg pub_key "$data_loader_snowflake_user_pub_key" \
  --arg priv_key "$data_loader_snowflake_user_priv_key" \
  '{"data_loader_snowflake_user_pub_key":$pub_key,"data_loader_snowflake_user_priv_key":$priv_key}'