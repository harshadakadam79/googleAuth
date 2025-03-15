from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
import os

SCOPES = ['https://www.googleapis.com/auth/drive']  # Scope for file access

def authenticate_google_drive():
    creds = None
    token_path = "token.json"

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = Flow.from_client_secrets_file(
                "client_secret.json",
                scopes=SCOPES,
                redirect_uri="http://127.0.0.1:8000/"  # Ensure it matches your Google Cloud settings
            )
            auth_url, _ = flow.authorization_url(prompt="consent")

            print(f"Please go to this URL and authorize access: {auth_url}")

            # After user grants permission, they'll be redirected to your redirect URI with a code.
            code = input("Enter the authorization code from the redirect URL: ")

            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(token_path, "w") as token:
            token.write(creds.to_json())
    
    return creds
