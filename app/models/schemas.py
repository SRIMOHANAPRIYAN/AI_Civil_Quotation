from pydantic import BaseModel, Field
from typing import List, Optional

# ---------------------------------------------------------
# DOMAIN: CIVIL ENGINEERING & WATERPROOFING
# ---------------------------------------------------------

class CivilServiceItem(BaseModel):
    service_category: str = Field(
        ..., 
        description="The type of service requested. e.g., 'Terrace Waterproofing', 'Cool Coating', 'Water Tank Coating'."
    )
    chemical_brand: str = Field(
        default="Standard", 
        description="The specific chemical or brand requested. e.g., 'Dr. Fixit', 'Asian Paints Damp Proof'. If not mentioned, return 'Standard'."
    )
    area_sqft: float = Field(
        ..., 
        description="The total area in square feet (sq ft) for this specific service."
    )
    
    # Notice: We do NOT extract price here. The Agent will fetch that from Sheet 2 later!
    rate_per_sqft: Optional[float] = None 
    warranty_years: Optional[int] = None

class CivilQuotationRequest(BaseModel):
    """The master schema for extracting the entire user request."""
    customer_name: str = Field(..., description="Name of the customer.")
    company_name: Optional[str] = Field(default="N/A", description="Customer's company, if provided.")
    email: Optional[str] = Field(default="N/A", description="Customer's email address.")
    phone: Optional[str] = Field(default="N/A", description="Customer's phone number.")
    location: str = Field(description="The city or location of the site, e.g., Dindigul")
    
    services: List[CivilServiceItem] = Field(
        ..., 
        description="A list of all civil services requested by the customer."
    )
    
    # Financial Telemetry (Kept from the core engine for FinOps)
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0
    total_cost_usd: Optional[float] = 0.0