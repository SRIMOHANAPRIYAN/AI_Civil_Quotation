from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=SCOPES
)

docs_service = build('docs', 'v1', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

print("Google Cloud Connected Successfully")