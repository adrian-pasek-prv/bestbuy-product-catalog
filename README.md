# bestbuy-product-catalog
A data engineering project that fetches data from api.bestbuy.com, stores it in Amazon S3, stages it in Snowflake, and models it with DBT to provide a comprehensive look at BestBuy product catalog.

## How to set up infrastructure
- `terraform plan`
- `terraform apply -var-file="vars.tfvars"`
- `terraform output -json > ./infrastructure.json`
