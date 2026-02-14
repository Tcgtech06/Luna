FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements_fastapi.txt .
RUN pip install --no-cache-dir -r requirements_fastapi.txt

# Copy application files
COPY main.py .
COPY static ./static

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Set environment variable for Hugging Face
ENV GRADIO_SERVER_NAME="0.0.0.0"

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
