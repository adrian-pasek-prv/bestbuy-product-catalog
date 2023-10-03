# football-leagues-data-pipeline
A data engineering project that fetches football data from www.api-football.com, stores it in Amazon S3, stages it in Snowflake, and models it with DBT to provide a comprehensive data warehouse for football leagues across Europe.

## How to set up infrastructure
- `terraform plan`
- `terraform apply -var-file="vars.tfvars"`
- `terraform output -json > ./infrastructure.json`