##############################################
####### DATA_LOADER USER, ROLE AND GRANTS ####
##############################################
##############################################


data "external" "data_loader_snowflake_user_keys" {
  program = ["bash", "keys_export.sh"]

}

resource "snowflake_user" "data_loader_user" {
  name = "DATA_LOADER"
  default_role = snowflake_role.data_loader.name
  default_warehouse = snowflake_warehouse.snowflake_wh.name
  # Snowflake requires public key without a header and footer
  rsa_public_key = data.external.data_loader_snowflake_user_keys.result.data_loader_snowflake_user_pub_key
  
}

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
  privileges = ["DELETE", "INSERT", "TRUNCATE", "SELECT"]
  role_name = snowflake_role.data_loader.name
  on_schema_object {
    all {
      object_type_plural = "TABLES"
      in_schema = "${snowflake_database.snowflake_raw_db.name}.PUBLIC"
    }
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