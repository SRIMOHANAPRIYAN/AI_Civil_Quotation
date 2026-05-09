import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive"]

def clear_service_account_drive():
    print("🔌 Authenticating into invisible Service Account...")
    
    # 1. Connect to the Service Account
    base_dir = os.path.abspath(os.path.dirname(__file__))
    creds_path = os.path.join(base_dir, "credentials.json")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)

    # 2. Find ALL files owned by this Service Account
    print("🔍 Scanning hidden drive for orphaned files...")
    
    # 'me' in owners ensures we only look at files the SA created and owns
    results = drive_service.files().list(q="'me' in owners", pageSize=1000).execute()
    files = results.get('files', [])

    if not files:
        print("✨ The invisible drive is already completely empty!")
    else:
        print(f"🗑️ Found {len(files)} files hoarding your storage! Deleting them now...")
        for f in files:
            try:
                drive_service.files().delete(fileId=f['id']).execute()
                print(f"  ❌ Deleted: {f['name']}")
            except Exception as e:
                print(f"  ⚠️ Could not delete {f['name']}: {e}")
                
        print("✅ BINGO! Service Account storage is 100% cleared and ready to work.")

if __name__ == "__main__":
    clear_service_account_drive()