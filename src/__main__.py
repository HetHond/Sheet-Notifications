import os
import json

# SMS imports
import vonage

# Local imports
from .sheets_client import get_gspread_client_with_auth
from .monitor import start_monitoring

# Constants
CONFIG_PATH = './config/config.json'
GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_config():
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)


if __name__ == "__main__":
    config = get_config()

    # Google Sheets Initialization
    google_credentials_path = os.environ.get('GOOGLE_CREDENTIALS_PATH')
    google_client = get_gspread_client_with_auth(google_credentials_path, GOOGLE_SHEETS_SCOPES)

    # Vonage Initialization
    vonage_api_key = os.environ.get('VONAGE_API_KEY')
    vonage_api_secret = os.environ.get('VONAGE_API_SECRET')
    vonage_client = vonage.Client(key=vonage_api_key, secret=vonage_api_secret)
    start_monitoring(google_client, vonage.Sms(vonage_client), config['spreadsheets'])
    