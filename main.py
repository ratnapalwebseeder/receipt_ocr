import asyncio
import logging
import os

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from services import extract_receipt, ocr_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("receipt_ocr")

API_KEY = os.environ.get("API_KEY")  # Get API key from .env file

app = FastAPI()

def verify_api_key(api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Health check
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Backend Status</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #f4f4f4; }
                h1 { color: #2c3e50; }
                a { text-decoration: none; color: white; background-color: #007BFF; padding: 10px 20px; border-radius: 5px; }
                a:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <h1>🚀 Everything is working!</h1>
            <p>Welcome to the Python World</p>
            <a href="/docs">Go to API Docs</a>
        </body>
    </html>
    """
    return html_content

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


