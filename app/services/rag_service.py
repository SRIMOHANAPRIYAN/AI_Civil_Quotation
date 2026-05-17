import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

# Setup Google Sheets Scopes & Authentication
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

def fetch_rate_and_warranty(service_category: str, chemical_brand: str) -> dict:
    """
    RAG Retrieval: Searches 'Master Rates' for the correct rate and warranty.
    """
    try:
        client = get_google_client()
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        
        # Make sure this matches the exact tab name at the bottom of your Google Sheet
        sheet = client.open_by_key(sheet_id).worksheet("Master Rates") 
        records = sheet.get_all_records()

        # Step 1: Try to find an exact match for both Category and Brand
        for row in records:
            sheet_category = str(row.get('Category', '')).strip().lower()
            # UPDATED to match your exact header: "Chemical / Solution Name"
            sheet_brand = str(row.get('Chemical / Solution Name', '')).strip().lower() 
            
            if sheet_category == service_category.lower() and sheet_brand == chemical_brand.lower():
                # UPDATED to match exact header: "Rate per Sq.Ft (₹)"
                rate = float(row.get('Rate per Sq.Ft (₹)', 0.0))
                warranty = int(row.get('Warranty (Years)', 0))
                print(f"RAG Match Found: {chemical_brand} at ₹{rate}/sqft")
                return {"rate_per_sqft": rate, "warranty_years": warranty}

        # Step 2: Fallback to 'Standard' if specific brand isn't found
        print(f"Specific brand '{chemical_brand}' not found. Searching for 'Standard' base rate...")
        for row in records:
            sheet_category = str(row.get('Category', '')).strip().lower()
            sheet_brand = str(row.get('Chemical / Solution Name', '')).strip().lower()
            
            if sheet_category == service_category.lower() and sheet_brand == 'standard':
                rate = float(row.get('Rate per Sq.Ft (₹)', 0.0))
                warranty = int(row.get('Warranty (Years)', 0))
                print(f"RAG Fallback Found: Standard {service_category} at ₹{rate}/sqft")
                return {"rate_per_sqft": rate, "warranty_years": warranty}

        print(f"RAG Failure: Could not find pricing for {service_category}.")
        return {"rate_per_sqft": 0.0, "warranty_years": 0}

    except Exception as e:
        print(f"Google Sheets API Error: {e}")
        return {"rate_per_sqft": 0.0, "warranty_years": 0}