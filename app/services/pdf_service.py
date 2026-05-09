# import os
# import pdfkit
# from flask import render_template
# from datetime import datetime
# import uuid

# def generate_pdf_from_payload(quotation_data: dict, filename: str) -> str:
#     print(f"Initializing PDF Generation for {quotation_data.get('customer_name')}...")
    
#     # Ensure the exports folder exists
#     export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "exports")
#     os.makedirs(export_dir, exist_ok=True)
    
#     output_path = os.path.join(export_dir, filename)

#     # Generate a unique quotation number and date if they don't exist
#     if 'quotation_number' not in quotation_data:
#         quotation_data['quotation_number'] = f"QTN-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:6].upper()}"
#     if 'date' not in quotation_data:
#         quotation_data['date'] = datetime.now().strftime("%B %d, %Y")

#     rendered_html = render_template("quotation_pdf.html", data=quotation_data)
#     options = {
#         'page-size': 'A4',
#         'margin-top': '0.75in',
#         'margin-right': '0.75in',
#         'margin-bottom': '0.75in',
#         'margin-left': '0.75in',
#         'encoding': "UTF-8",
#         'enable-local-file-access': None
#     }

#     # Convert HTML string to PDF
#     pdfkit.from_string(rendered_html, output_path, options=options)
#     print(f"PDF successfully generated: {output_path}")
#     return f"static/exports/{filename}"

# import os
# import pdfkit
# from flask import render_template
# from datetime import datetime
# import uuid

# def generate_pdf_from_payload(quotation_data: dict, filename: str) -> str:
#     print(f"Initializing PDF Generation for {quotation_data.get('customer_name')}...")
    
#     # 1. Setup absolute paths so wkhtmltopdf can find the files
#     base_dir = os.path.dirname(os.path.dirname(__file__))
#     export_dir = os.path.join(base_dir, "static", "exports")
#     os.makedirs(export_dir, exist_ok=True)
#     output_path = os.path.join(export_dir, filename)

#     header_path = os.path.join(base_dir, "templates", "header.html")
#     footer_path = os.path.join(base_dir, "templates", "footer.html")

#     # 2. Render the main body HTML
#     rendered_html = render_template("quotation_pdf.html", data=quotation_data)

#     # 3. PDF Configuration Options (Notice the new header/footer margins & paths)
#     options = {
#         'page-size': 'A4',
#         'margin-top': '35mm',       # Leaves 3.5cm of blank space at the top for the Header
#         'margin-bottom': '30mm',    # Leaves 3cm of blank space at the bottom for the Footer
#         'margin-right': '20mm',
#         'margin-left': '20mm',
#         'header-html': header_path,
#         'footer-html': footer_path,
#         'header-spacing': '5',      # Gap between header and content
#         'footer-spacing': '5',      # Gap between content and footer
#         'encoding': "UTF-8",
#         'enable-local-file-access': None
#     }

#     # 4. Convert HTML string to PDF
#     pdfkit.from_string(rendered_html, output_path, options=options)
#     print(f"PDF successfully generated: {output_path}")
    
#     return f"static/exports/{filename}"

import os
import io
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials

# We need permissions for both Docs (to edit text) and Drive (to copy/export files)
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]

def get_google_services():
    """Authenticates and returns the Docs and Drive API clients."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    creds_path = os.path.join(base_dir, "credentials.json")
    
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    docs_service = build('docs', 'v1', credentials=creds)
    return drive_service, docs_service

def generate_pdf_from_payload(quotation_data: dict, filename: str) -> str:
    print(f"Initializing Google Docs Automation for {quotation_data.get('customer_name')}...")
    
    # --- PASTE YOUR GOOGLE DOC ID HERE ---
    TEMPLATE_DOC_ID = "1l6SzyBvC-KwLzd_v9CrLEagkUemI8aGvaJ-oEBr1rEY" 
    TEMP_FOLDER_ID = "1uz-DWpmO5Eok8st6fmFzxDIP6k-etrjW"
    drive_service, docs_service = get_google_services()
    
    # 1. Make a temporary copy of the Master Template
    # copy_metadata = {'name': f"Temp_Quote_{quotation_data['quotation_number']}}",'parents': [TEMP_FOLDER_ID]
    copy_metadata = {
        'name': f"Temp_Quote_{quotation_data['quotation_number']}",
        'parents': [TEMP_FOLDER_ID]
    }               
    copied_doc = drive_service.files().copy(fileId=TEMPLATE_DOC_ID, body=copy_metadata).execute()
    new_doc_id = copied_doc.get('id')
    
    try:
        # Extract the first service to map to the template
        service = quotation_data['services'][0] if quotation_data['services'] else {}
        
        # 2. Define exactly what text to find and replace
        # This matches the {{tags}} you put in your Google Doc!
        replacements = {
            "{{Date}}": datetime.now().strftime("%d.%m.%Y"),
            "{{Name}}": quotation_data.get('customer_name', ''),
            "{{Location}}": quotation_data.get('location', 'Site Location'), # We will update schema next
            "{{Category}}": service.get('service_category', ''),
            "{{sq}}": str(service.get('area_sqft', 0)),
            "{{r}}": str(service.get('rate_per_sqft', 0)),
            "{{TM}}": str(service.get('service_total_price', 0)),
            "{{y}}": str(service.get('warranty_years', 0))
        }

        # Build the batchUpdate requests
        requests = []
        for tag, replacement_text in replacements.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {'text': tag, 'matchCase': True},
                    'replaceText': replacement_text
                }
            })

        # 3. Execute the text replacement inside the Google Doc
        docs_service.documents().batchUpdate(
            documentId=new_doc_id, 
            body={'requests': requests}
        ).execute()

        print("Text successfully injected into Google Doc.")

        # 4. Download the newly edited Doc as a PDF
        request = drive_service.files().export_media(fileId=new_doc_id, mimeType='application/pdf')
        
        base_dir = os.path.dirname(os.path.dirname(__file__))
        export_dir = os.path.join(base_dir, "static", "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        output_path = os.path.join(export_dir, filename)
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        with open(output_path, 'wb') as f:
            f.write(fh.getvalue())
            
        print(f"PDF downloaded and saved to: {output_path}")
        
    finally:
        # 5. Clean up: Delete the temporary Google Doc so your Drive doesn't get cluttered
        drive_service.files().delete(fileId=new_doc_id).execute()
        print("Temporary Google Doc deleted.")

    return f"static/exports/{filename}"