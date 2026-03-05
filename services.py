import json
import re
import os
import requests
from imgocr import ImgOcr

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

def ocr_image(image_path: str):
    """Extract text from receipt image using ImgOcr."""
    print(f"Extracting data from: {image_path}")
    # Initialize OCR
    m = ImgOcr(use_gpu=False, is_efficiency_mode=True)
    result = m.ocr(image_path)
    
    data = ""
    for i in result:
        data += i['text'] + "\n"
    return data

def extract_receipt(receipt_text: str):
    """Send OCR text to LLM and extract structured receipt data."""
    print("Getting response from the LLM...")

    # FIXED: Added missing quote after invoice_number
    prompt = f'''You are a JSON data extractor. Extract receipt data into the exact JSON format below.

    RULES:
    - Output ONLY valid JSON
    - Use null if field not found
    - All prices as strings (e.g., "10.50") 
    - Date format (YYYY-MM-DD), Time format (HH:MM)

    JSON SCHEMA:
    {{
      "store_name": null,
      "invoice_number": null,
      "customer_name": null,
      "date": null,
      "order_time": null,
      "final_total": null,
      "payment_method": null
    }}

    RECEIPT TEXT:
    {receipt_text}
    '''

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": "granite3.3:latest",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            }
        )

        if response.status_code != 200:
            return {"error": f"LLM Service Error {response.status_code}"}

        result = response.json().get("response", "")
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        
        if json_match:
            return json.loads(json_match.group())
        return json.loads(result)

    except Exception as e:
        return {"error": str(e)}