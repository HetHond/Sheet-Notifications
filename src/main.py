# Standard library imports
import argparse
import json
import os
import sys

# Third-party imports
import vonage
from jsonschema import validate
from jsonschema.exceptions import ValidationError

# Local application/library specific imports
from .constants import GOOGLE_SHEETS_SCOPES, CONFIG_SCHEMA
from .monitor import start_monitoring
from .sheets_client import (
    get_gspread_client_with_auth,
    get_gspread_with_service_account
)


def get_config(config_path):
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Configuration file not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error decoding the configuration file.")
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Sheet Notifications Application")
    parser.add_argument('--config', help='Path to the config file', default='./config.json')
    parser.add_argument('--service-account', action='store_true', help='Use a service account instead of OAuth')
    parser.add_argument('--service-account-path',
                        help='Path to the service account key json',
                        default='./service-account-credentials.json')
    parser.add_argument('--google-credentials-path',
                        help='Path to the Google credentials file',
                        default=os.environ.get('GOOGLE_CREDENTIALS_PATH'))
    parser.add_argument('--vonage-api-key', help='Vonage api key', default=os.environ.get('VONAGE_API_KEY'))
    parser.add_argument('--vonage-api-secret', help='Vonage api secret', default=os.environ.get('VONAGE_API_SECRET'))
    return parser.parse_args()


def main():
    args = parse_args()
    config = get_config(args.config)
    
    # Validate config data
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        print(f"Configuration validation error: ", e)
        sys.exit(1)
    
    # Google Sheets Initialization
    if args.service_account:
        try:
            google_client = get_gspread_with_service_account(args.service_account_path, GOOGLE_SHEETS_SCOPES)
        except FileNotFoundError:
            print("Service account credentials file not found.")
            sys.exit(1)
        pass
    else:
        google_credentials_path = args.google_credentials_path
        if not google_credentials_path:
            print("Missing Google credentials path.")
            sys.exit(1)
        google_client = get_gspread_client_with_auth(args.google_credentials_path, GOOGLE_SHEETS_SCOPES)
    
    # Vonage Initialization
    vonage_api_key = args.vonage_api_key
    vonage_api_secret = args.vonage_api_secret
    if not vonage_api_key:
        print('Missing Vonage api key')
        sys.exit(1)
    
    if not vonage_api_secret:
        print('Missing Vonage api secret')
    vonage_client = vonage.Client(key=args.vonage_api_key, secret=args.vonage_api_secret)
    start_monitoring(google_client, vonage.Sms(vonage_client), config['spreadsheets'], config['interval'])
    