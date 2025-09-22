# Receipt OCR API

A FastAPI-based service that extracts structured data from receipt images using OCR and LLM-powered data extraction.

## Overview

This project provides a REST API that processes uploaded receipt images and returns structured information in json.

## How It Works

The API follows a two-stage processing pipeline:

1. **OCR Stage**: When you upload a receipt image, the system first uses `imgocr` library to extract all text content from the image.

2. **Data Extraction Stage**: The extracted text is then processed by a local LLM (using Ollama with the Granite model) that intelligently identifies and structures the key information from the receipt. The model understands various receipt formats and can handle different layouts, currencies, and merchant styles and gives `JSON` reponse.

The entire process runs asynchronously, allowing the API to handle multiple requests efficiently without blocking operations.


## Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com/download) installed and running locally
- [Granite3.3:8B](https://ollama.com/library/granite3.3:8b) model available in your Ollama instance

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/ratnapalwebseeder/receipt_ocr.git
cd receipt-ocr
```

2. **Set up a virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Give Execute Permission**:
```bash
chmod +x run.sh
```

5. **Start the API server**:
```bash
./run.sh
```
> ⚠️ If `./run.sh` command not working for you then use this command to run:
```bash
uvicorn main:app --host 0.0.0.0 --port 6395
```
The API will be available at `http://localhost:6395/docs`



