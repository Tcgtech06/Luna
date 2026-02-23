FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend files
COPY main.py .
COPY model_manager.py .
COPY google_file_manager.py .
COPY file_storage.py .

# Create necessary directories
RUN mkdir -p static chroma_db

# Expose port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]
