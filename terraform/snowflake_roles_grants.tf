##############################################
####### DATA_LOADER USER, ROLE AND GRANTS ####
##############################################
##############################################

# Generate a SSH key-pair for DATA_LOADER user
resource "tls_private_key" "data_loader_ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Export key files to ../config so it will be readable by Airflow
resource "terraform_data" "data_loader_ssh_key_file" {

  provisioner "local-exec" { 
    command = <<-EOT
      echo "${tls_private_key.data_loader_ssh_key.private_key_pem}" > ../config/data_loader_snowflake_user.pem
      chmod 400 ../config/data_loader_snowflake_user.pem
      echo "${trimspace(tls_private_key.data_loader_ssh_key.public_key_pem)}" > ../config/data_loader_snowflake_user.pub
      chmod 400 ../config/data_loader_snowflake_user.pub
      EOT
  }
}

# Snowflake requires public key without a header and footer. This script will remove them.
data "external" "data_loader_snowflake_user_pub_key_without_header" {
  program = ["bash", "data_loader_key_remove_header.sh"]
}

resource "snowflake_user" "data_loader_user" {
  name = "DATA_LOADER"
  default_role = snowflake_role.data_loader.name
  default_warehouse = snowflake_warehouse.snowflake_wh.name
  # Take header and footer-less keys
  rsa_public_key = data.external.data_loader_snowflake_user_pub_key_without_header.result.data_loader_snowflake_user_pub_key
  
}

resource "snowflake_role" "data_loader" {
  name = "DATA_LOADER"
  comment = "Role for copying into raw table from S3 bucket"
}

# Assign role to user
resource "snowflake_role_grants" "data_loader_role_assignment" {
  role_name = snowflake_role.data_loader.name
  users = [snowflake_user.data_loader_user.name]
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