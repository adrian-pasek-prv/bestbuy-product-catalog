#!/bin/bash

# Extract the keys without header and footer and remove new line breaks because JSON doesn't process them
data_loader_snowflake_user_pub_key=$(sed -n '/-----BEGIN PUBLIC KEY-----/,/-----END PUBLIC KEY-----/p' ~/.ssh/data_loader_snowflake_user.pub | sed '1d;$d' | tr -d '\n')
data_loader_snowflake_user_priv_key=$(sed -n '/-----BEGIN PRIVATE KEY-----/,/-----END PRIVATE KEY-----/p' ~/.ssh/data_loader_snowflake_user.p8 | sed '1d;$d' | tr -d '\n')

printf '{"data_loader_snowflake_user_pub_key":"%s","data_loader_snowflake_user_priv_key":"%s"}' "$data_loader_snowflake_user_pub_key" "$data_loader_snowflake_user_priv_key"

