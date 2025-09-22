import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Header, HTTPException, UploadFile

from services import extract_receipt, ocr_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("receipt_ocr")

load_dotenv()  # Load .env file
API_KEY = os.getenv("RECEIPT_API_KEY")  # Get API key from .env file
API_KEY = '123'

app = FastAPI()

def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Health check
@app.get("/")
def home():
    return {"message": "Receipt OCR API is running!"}


@app.post("/process-receipt")
async def process_receipt(
    file: UploadFile = File(...),
    api_key: str = Header(..., alias="api-key")
):
    logger.info(f"Received request for file: {file.filename}")
    verify_api_key(api_key)

    if not file.content_type.startswith("image/"):
        logger.warning(f"Uploaded File is not an image: {file.filename.rsplit(".")}")
        raise HTTPException(status_code=400, detail="File must be an image")

    file_bytes = await file.read()

    loop = asyncio.get_event_loop()
    ocr_text = await loop.run_in_executor(None, ocr_image, file_bytes)

    extracted_data = extract_receipt(ocr_text)
    return extracted_data


