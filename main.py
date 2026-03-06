import asyncio
import logging
import os
import uuid
import shutil

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
    verify_api_key(api_key)
    
    temp_path = f"temp_{uuid.uuid4()}.jpg"
    try:
        # 1. Reset file pointer to the beginning
        await file.seek(0) 
        
        # 2. Write the content manually to ensure it's fully flushed to disk
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
            
        with open(temp_path, "wb") as f:
            f.write(content)

        # 3. Run OCR
        loop = asyncio.get_event_loop()
        ocr_text = await loop.run_in_executor(None, ocr_image, temp_path)
        
        return extract_receipt(ocr_text)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


