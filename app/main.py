import os
import uuid
from datetime import datetime
import threading
from pydantic import ValidationError
from flask import Flask, request, render_template, send_file, session
from app.services.llm_service import extract_quotation_data, transcribe_audio
from app.services.security_service import check_prompt_security
from app.services.enrichment_service import enrich_extracted_items
from app.services.calc_service import calculate_quotation_totals
from app.services.pdf_service import generate_pdf_from_payload
from app.services.storage_service import append_to_ledger
from app.models.schemas import CivilQuotationRequest

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "civil_engineering_secret_key_123"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# --- MULTIMODAL FUSION ROUTE ---
@app.route("/api/generate-fusion", methods=["POST"])
async def generate_fusion():
    try:
        # 1. Catch Text, Audio, and Routing Flag
        text_data = request.form.get("text_data", "").strip()
        audio_file = request.files.get("voice_data")
        
        push_to_sheets = request.form.get("push_to_sheets") == "true"
        session['push_to_sheets'] = push_to_sheets

        transcribed_text = ""

        # 2. Process Audio via Whisper
        if audio_file:
            filepath = os.path.join("temp_voice.webm")
            audio_file.save(filepath)
            print("Processing Audio via Whisper...")
            transcribed_text = await transcribe_audio(filepath) 
            if os.path.exists(filepath):
                os.remove(filepath)

        # 3. Context Fusion
        combined_prompt = f"User Typed Context: {text_data} | User Spoken Context: {transcribed_text}".strip()

        if combined_prompt == "User Typed Context:  | User Spoken Context:":
            return {"error": "Please provide text or voice data."}, 400

        print(f"Fused Context Ready: {combined_prompt}")
        
        # 4. Security Firewall
        is_safe = await check_prompt_security(combined_prompt)
        if not is_safe:
            return {"error": "Security Alert: Malicious prompt detected. Request blocked."}, 400

        # 5. LLM Extraction (Using Civil Schema)
        extracted_data = await extract_quotation_data(combined_prompt)
        if not extracted_data.services:
            return {"error": "Could not identify any valid civil engineering services in your request."}, 400

        # 6. RAG Enrichment (Fetch prices from Google Sheets)
        extracted_data = enrich_extracted_items(extracted_data)

        # 7. Strict Catalog Check
        for service in extracted_data.services:
            if not service.rate_per_sqft or service.rate_per_sqft <= 0:
                return {"error": f"Invalid Request: Pricing for '{service.service_category}' not found in Master Rates."}, 400

        # Go to verification page
        json_str = extracted_data.model_dump_json(indent=4)
        return render_template("verify.html", json_data=json_str)

    except Exception as e:
        print(f"Fusion API Error: {e}")
        return {"error": str(e)}, 500

# --- FINAL GENERATION ROUTE ---
@app.route("/generate", methods=["POST"])
def generate():
    edited_json = request.form.get("edited_json")
    
    try:
        # 1. Validate the edited JSON against our Civil Schema
        validated_data = CivilQuotationRequest.model_validate_json(edited_json)
        
        # 2. Run the math (Area * Rate)
        final_quotation = calculate_quotation_totals(validated_data)
        
        # --- NEW FIX: Generate Quotation ID here ---
        if 'quotation_number' not in final_quotation:
            final_quotation['quotation_number'] = f"QTN-{datetime.now().strftime('%Y%m')}-{str(uuid.uuid4())[:6].upper()}"
        
        # 3. Generate PDF
        pdf_filename = f"{final_quotation['quotation_number']}.pdf"
        pdf_path = generate_pdf_from_payload(final_quotation, pdf_filename)
        
        # 4. Push to Google Sheets Ledger (Background Thread)
        push_to_sheets = session.get('push_to_sheets', True)
        
        if push_to_sheets:
            print("Routing data to Google Sheets Ledger...")
            
            # Extract ALL info for the 8 ledger columns
            quotation_number = final_quotation['quotation_number']
            cust_name = final_quotation['customer_name']
            total_area = sum([s['area_sqft'] for s in final_quotation['services']])
            category = final_quotation['services'][0]['service_category'] if len(final_quotation['services']) == 1 else "Mixed Services"
            subtotal = final_quotation['subtotal']
            gst_amount = final_quotation['gst_amount']
            grand_total = final_quotation['grand_total']
            
            threading.Thread(target=append_to_ledger, args=(
                quotation_number, 
                cust_name, 
                category, 
                total_area, 
                subtotal, 
                gst_amount, 
                grand_total
            )).start()
        else:
            print("Skipped Google Sheets save.")

        print(f"Dispatching Final PDF: {pdf_filename}")
        
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
        
    except ValidationError as e:
        return {"error": f"JSON Syntax Error: Details: {e}"}, 400
    except Exception as e:
        return {"error": f"Generation Error: {e}"}, 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)