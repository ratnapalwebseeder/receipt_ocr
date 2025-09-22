import json
import re

import requests
from imgocr import ImgOcr


def ocr_image(image_path: str):
    """Extract text from receipt image using ImgOcr."""
    print("Extracting data from the image...")
    m = ImgOcr(use_gpu=False, is_efficiency_mode=True)
    result = m.ocr(image_path)
    data = ""
    for i in result:
        data += i['text'] + "\n"
    # print(data)
    return data


def extract_receipt(receipt_text: str):
    """Send OCR text to LLM and extract structured receipt data."""
    print("Getting response from the LLM...")

    prompt = f'''You are a JSON data extractor. Extract receipt data into the exact JSON format below.

    RULES:
    - Output ONLY valid JSON and only json schema provided below
    - Use null if field not found
    - All prices as strings (e.g., "10.50") only number
    - All quantities should be numeric strings (e.g., "2")
    - Date format (YYYY-MM-DD)
    - Time format (HH:MM)

    JSON SCHEMA:
    {{
      "store_name": null,
      "invoice_number: null,
      "customer_name": null,
      "date": null,
      "order_time": null,
      "final_total": null,
      "payment_method": null
    }}

    Extract and return JSON for this receipt:
    <<<
    {receipt_text}
    >>>
    You are a JSON data extractor. Extract receipt data into the exact JSON format below.

    RULES:
    - Output ONLY valid JSON and only json schema provided below
    - Use null if field not found
    - All prices as strings (e.g., "10.50") only number
    - All quantities should be numeric strings (e.g., "2")
    - Date format (YYYY-MM-DD)
    - Time format (HH:MM)

    JSON SCHEMA:
    {{
      "store_name": null,
      "invoice_number: null,
      "customer_name": null,
      "date": null,
      "order_time": null,
      "final_total": null,
      "payment_method": null
    }}
    '''

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "granite3.3:latest",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0}
            }
        )

        if response.status_code != 200:
            return {"error": f"HTTP Error {response.status_code}"}

        response_data = response.json()
        result = response_data["response"]

        # Try to extract JSON from response
        json_match = re.search(r"\{.*\}", result, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            return json.loads(result)

    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing error: {str(e)}", "raw_result": result}
    except Exception as e:
        return {"error": str(e)}
