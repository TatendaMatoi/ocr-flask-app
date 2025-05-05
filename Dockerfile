# 1. Use official Python base image
FROM python:3.11-slim

# 2. Install system dependencies (Tesseract & Poppler)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 3. Set working directory in container
WORKDIR /app

# 4. Copy your app files into the container
COPY . .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose port 5000 (Flask default)
EXPOSE 5000

# 7. Run the app
CMD ["python", "app.py"]
