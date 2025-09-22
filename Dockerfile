FROM python:3.12-slim

# Security updates
RUN apt-get update && apt-get upgrade -y

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 6395

# Production uvicorn settings
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6395", "--workers", "2"]