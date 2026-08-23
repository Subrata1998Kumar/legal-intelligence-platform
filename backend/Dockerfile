# Use an official lightweight Python runtime
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /workspace

# Install system dependencies required for PDF processing and OCR
# - tesseract-ocr: OCR engine for scanned files
# - tesseract-ocr-eng: English language pack for Tesseract
# - poppler-utils: PDF-to-image converter required for pyimages/pdf2image
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy backend Python dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY . .

# Expose the FastAPI gateway port
EXPOSE 8000

# Execute FastAPI utilizing Uvicorn server on port 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]