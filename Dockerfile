# Step 1: Base image
FROM python:3.11-slim

# Step 2: Install system dependencies (Tesseract + poppler-utils + build tools)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    gcc \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Set working directory
WORKDIR /app

# Step 4: Copy project files
COPY . .

# Step 5: Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Step 6: Expose Flask port
EXPOSE 5000

# Step 7: Run the app
CMD ["python", "app.py"]
