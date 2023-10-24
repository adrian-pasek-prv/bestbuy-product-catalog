import json
import logging
import argparse


def convert_to_airflow_json(terraform_json_key, terraform_json, airflow_json):
    
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    
    with open(terraform_json, 'r') as f:
        json_file = json.load(f)
        infrastructure = json_file[terraform_json_key]["value"]
        
        airflow = {}
        for key, value in infrastructure.items():
            airflow[key] = value
        
        # Save connections to JSON file
        with open(airflow_json, 'w') as f:
            json.dump(airflow, f)

    logging.info(f"Saved Airflow JSON file to '{airflow_json}' successfully")

def main():
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(description='Converts Terraform JSON file to Airflow JSON file.')

    # Define the arguments you want to accept
    parser.add_argument('terraform_json_key', type=str, help='Terraform JSON key to extract piece of infrastructure from')
    parser.add_argument('terraform_json', type=str, help='Path to Terraform JSON file')
    parser.add_argument('airflow_json', type=str, help='Path to Airflow JSON file to save.')

    # Parse the command-line arguments
    args = parser.parse_args()

    
    convert_to_airflow_json(args.terraform_json_key, args.terraform_json, args.airflow_json)


if __name__ == '__main__':
    main()

