##############################################
####### DATA_LOADER ROLE AND GRANTS ##########
##############################################
##############################################

resource "snowflake_role" "data_loader" {
  name = "DATA_LOADER"
  comment = "Role for copying into raw table from S3 bucket"
}

# Warehouse grants
resource "snowflake_grant_privileges_to_role" "data_loader_warehouse_grant" {
  privileges = ["USAGE"]
  role_name = snowflake_role.data_loader.name
  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.snowflake_wh.name
  }
}

# Database grants
resource "snowflake_grant_privileges_to_role" "data_loader_database_grant" {
  privileges = [ "USAGE"]
  role_name = snowflake_role.data_loader.name
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.snowflake_raw_db.name
  }
}

# Schema grants
resource "snowflake_grant_privileges_to_role" "data_loader_schema_grant" {
  privileges = [ "USAGE", "CREATE TABLE"]
  role_name = snowflake_role.data_loader.name
  on_schema {
    schema_name = "${snowflake_database.snowflake_raw_db.name}.PUBLIC"
  }
}

# Table grants
resource "snowflake_grant_privileges_to_role" "data_loader_table_grant" {
  privileges = [ "DELETE", "INSERT", "TRUNCATE"]
  role_name = snowflake_role.data_loader.name
  on_schema_object {
    object_type = "TABLE"
    object_name = "${snowflake_database.snowflake_raw_db.name}.PUBLIC.${snowflake_table.snowflake_raw_table.name}"
  }
}

# File format grants
resource "snowflake_grant_privileges_to_role" "data_loader_file_format_grant" {
  privileges = [ "USAGE" ]
  role_name = snowflake_role.data_loader.name
  on_schema_object {
    object_type = "FILE FORMAT"
    object_name = "${snowflake_database.snowflake_raw_db.name}.PUBLIC.${snowflake_file_format.json_file_format.name}"
  }
}

# Stage grants
resource "snowflake_grant_privileges_to_role" "data_loader_stage_grant" {
  privileges = [ "USAGE"]
  role_name = snowflake_role.data_loader.name
  on_schema_object {
    object_type = "STAGE"
    object_name = "${snowflake_database.snowflake_raw_db.name}.PUBLIC.${snowflake_stage.stage.name}"
  }
}