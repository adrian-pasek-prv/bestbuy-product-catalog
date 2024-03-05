resource "snowflake_warehouse" "snowflake_wh" {
  name = var.snowflake_warehouse
  comment = "General XS warehouse managed by Terraform"
  warehouse_size = "X-SMALL"
  auto_resume = true
  auto_suspend = 60
  initially_suspended = true 
}

resource "snowflake_database" "snowflake_raw_db" {
  name = var.snowflake_raw_db
  data_retention_time_in_days = 0
  comment = "Database for raw JSON data"
}

resource "snowflake_table" "snowflake_raw_table" {
  name = var.snowflake_raw_table
  database = snowflake_database.snowflake_raw_db.name
  schema = "PUBLIC"
  comment = "Table for raw JSON data"
  column {
    name = "JSON_DATA"
    type = "VARIANT"
    nullable = true
  }
  column {
    name = "FILENAME"
    type = "TEXT"
    nullable = true
  }
  column {
    name = "LOAD_DATE"
    type = "TEXT"
    nullable = true
  }
}