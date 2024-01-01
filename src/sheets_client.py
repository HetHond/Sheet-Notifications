import gspread
from google_auth_oauthlib.flow import InstalledAppFlow


def get_gspread_client_with_auth(credentials_path, scopes):
    # Load OAuth credentials
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
    credentials = flow.run_local_server(port=0)

    # Create a gspread client
    return gspread.authorize(credentials)
