import os
from openai import AsyncOpenAI
from app.models.schemas import CivilQuotationRequest
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. AI Extraction (Text to Structured JSON)
async def extract_quotation_data(user_prompt: str) -> CivilQuotationRequest:
    print("Initiating AI Extraction Phase...")
    
    system_prompt = """
    You are an expert Civil Engineering and Construction Estimator AI.
    Your job is to extract quotation details from the user's input.
    
    RULES:
    1. Extract the customer's name, company, email, and phone if available.
    2. Extract a list of all services requested.
    3. For each service, identify the 'service_category' (e.g., Terrace Waterproofing, Cool Coating).
    4. For each service, identify the 'chemical_brand' (e.g., Dr. Fixit, Asian Paints). If none is specified, output "Standard".
    5. For each service, extract the 'area_sqft' as a number.
    6. Do NOT guess prices. The system will handle pricing separately.
    """

    try:
        # Using the newest model for perfect structured extraction
        completion = await client.beta.chat.completions.parse(
            # model="gpt-4o-2024-08-06",
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=CivilQuotationRequest,
        )

        extracted_data = completion.choices[0].message.parsed
        
        # Telemetry / FinOps tracking
        extracted_data.prompt_tokens = completion.usage.prompt_tokens
        extracted_data.completion_tokens = completion.usage.completion_tokens
        
        # Approximate Cost Calculation for GPT-4o
        cost_per_1k_prompt = 0.0025
        cost_per_1k_completion = 0.010
        total_cost = (extracted_data.prompt_tokens / 1000 * cost_per_1k_prompt) + \
                     (extracted_data.completion_tokens / 1000 * cost_per_1k_completion)
        extracted_data.total_cost_usd = round(total_cost, 6)

        print(f"Extraction Successful. Cost: ${extracted_data.total_cost_usd}")
        return extracted_data

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e


# 2. Audio Transcription (Voice to Text)
async def transcribe_audio(filepath: str) -> str:
    """
    Uses OpenAI Whisper to convert a webm/mp3 voice recording into text.
    """
    print("Sending audio to Whisper API...")
    try:
        with open(filepath, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        print(f"Transcription Success: '{transcript.text[:50]}...'")
        return transcript.text
    except Exception as e:
        print(f"Whisper Transcription Error: {e}")
        raise e