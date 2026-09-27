import os
import base64
from pathlib import Path
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
PROJECT_DIR = Path(__file__).resolve().parent

def authenticate_gmail():
    """Authenticates the user and returns the credentials."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = PROJECT_DIR / "token.json"
    credentials_path = PROJECT_DIR / "credentials.json"
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    "credentials.json is missing. Download an OAuth desktop-client file from Google Cloud."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            # This opens the browser for the user to authenticate
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with token_path.open("w") as token:
            token.write(creds.to_json())
    
    return creds

def send_email(to_email, subject, body):
    """Create and send an email message."""
    try:
        if not to_email or not subject or not body:
            return False, "Recipient, subject, and body are required."

        creds = authenticate_gmail()
        service = build("gmail", "v1", credentials=creds)
        
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to_email
        message["Subject"] = subject
        
        # Base64 encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {"raw": encoded_message}
        
        # Send the email
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        return True, f"Email sent successfully! (Message ID: {send_message.get('id', 'unknown')})"
        
    except Exception as error:
        return False, f"An error occurred while sending: {error}"
