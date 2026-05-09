from app.services.rag_service import fetch_rate_and_warranty

def enrich_extracted_items(extracted_data):
    print("Starting Agentic Enrichment Phase...")
    
    for service in extracted_data.services:
        print(f"Checking RAG for: {service.service_category} ({service.chemical_brand})")
        
        # Call our Google Sheets RAG Agent
        rag_data = fetch_rate_and_warranty(service.service_category, service.chemical_brand)
        
        # Inject the retrieved data into our Pydantic schema
        service.rate_per_sqft = rag_data.get("rate_per_sqft", 0.0)
        service.warranty_years = rag_data.get("warranty_years", 0)
        
    return extracted_data