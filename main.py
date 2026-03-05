import asyncio
import logging
import os
import tempfile
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from services import extract_receipt, ocr_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("receipt_ocr")

API_KEY = os.environ.get("API_KEY")
app = FastAPI()

def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<h1>🚀 OCR Service is Running</h1>"

@app.post("/process-receipt")
async def process_receipt(
    file: UploadFile = File(...),
    api_key: str = Header(..., alias="api-key")
):
    logger.info(f"Received request for file: {file.filename}")
    verify_api_key(api_key)

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # STEP 1: Save bytes to a temporary file path
    # ImgOcr requires a physical file path string.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # STEP 2: Pass the PATH to the OCR function
        loop = asyncio.get_event_loop()
        ocr_text = await loop.run_in_executor(None, ocr_image, tmp_path)

        # STEP 3: Extract and Return
        extracted_data = extract_receipt(ocr_text)
        return extracted_data

    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # STEP 4: Clean up the file so the server doesn't get full
        if os.path.exists(tmp_path):
            os.remove(tmp_path)