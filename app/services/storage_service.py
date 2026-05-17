import os
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_client():
    """Authenticates and returns the gspread client."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    creds_path = os.path.join(base_dir, "credentials.json")
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError("credentials.json not found! Please add it to the root folder.")
        
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)

def append_to_ledger(quotation_number: str, customer_name: str, service_category: str, total_area: float, subtotal: float, gst: float, grand_total: float):

    try:
        client = get_google_client()
        sheet_id = os.getenv("GOOGLE_SHEET_ID").strip()
        ledger_sheet = client.open_by_key(sheet_id).worksheet("Ledger")
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [
            current_date,           
            quotation_number,      
            customer_name,          
            service_category,       
            total_area,             
            subtotal,              
            gst,                    
            grand_total             
        ]
        
        ledger_sheet.append_row(new_row)
        print("Successfully saved all 8 columns to Google Sheets Ledger!")
        
    except Exception as e:
        print(f"Failed to save to Ledger: {e}")