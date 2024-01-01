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
    google_client = get_gspread_client_with_auth(config['google_credentials_path'], GOOGLE_SHEETS_SCOPES)

    # Vonage Initialization
    vonage_client = vonage.Client(key=config['vonage_api_key'], secret=config['vonage_api_secret'])
    start_monitoring(google_client, vonage.Sms(vonage_client), config['spreadsheets'])
    