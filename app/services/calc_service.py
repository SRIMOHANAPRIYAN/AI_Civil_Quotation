def calculate_quotation_totals(quotation_data):
    final_data = quotation_data.model_dump()
    subtotal = 0.0
    
    # 1. Calculate individual service totals
    for service in final_data["services"]:
        area = float(service.get("area_sqft", 0.0))
        rate = float(service.get("rate_per_sqft", 0.0))
        
        service_total = area * rate
        service["service_total_price"] = service_total # Save the row total
        
        subtotal += service_total
        
    # 2. Calculate Taxes (Assuming standard 18% GST for construction/chemicals)
    gst_amount = subtotal * 0.18
    grand_total = subtotal + gst_amount
    
    # 3. Append master financial totals to the dictionary
    final_data["subtotal"] = round(subtotal, 2)
    final_data["gst_amount"] = round(gst_amount, 2)
    final_data["grand_total"] = round(grand_total, 2)
    
    print(f"Math Complete: Subtotal ₹{final_data['subtotal']} | Grand Total ₹{final_data['grand_total']}")
    
    return final_data