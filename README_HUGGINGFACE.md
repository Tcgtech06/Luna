# Luna - AI Chatbot by TCG TECH

Luna is an intelligent AI chatbot powered by Google Gemini AI, built with FastAPI for deployment on Hugging Face Spaces.

## Features

- 🌙 Modern, responsive UI with dark/light theme toggle
- 💬 Real-time chat with typing indicators
- 📎 File and image upload support
- 🔄 Automatic model fallback for reliability
- 🎨 Beautiful gradient design

## Deployment on Hugging Face

### Method 1: Using Hugging Face Spaces UI

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose "Docker" as the SDK
4. Upload these files:
   - `main.py`
   - `requirements_fastapi.txt`
   - `Dockerfile`
   - `static/index.html`
5. Add your Gemini API key as a secret:
   - Go to Settings → Repository secrets
   - Add: `GEMINI_API_KEY` = your_api_key

### Method 2: Using Git

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy files
cp main.py Dockerfile requirements_fastapi.txt ./
cp -r static ./

# Commit and push
git add .
git commit -m "Deploy Luna chatbot"
git push
```

### Environment Variables

Set these in your Hugging Face Space settings:

- `GEMINI_API_KEY`: Your Google Gemini API key

## Local Development

```bash
# Install dependencies
pip install -r requirements_fastapi.txt

# Run the server
python main.py
```

Visit http://localhost:7860

## API Endpoints

- `GET /`: Main chat interface
- `POST /chat`: Send message and get response
- `POST /upload`: Upload files

## Tech Stack

- FastAPI
- Google Gemini AI
- LangChain
- HTML/CSS/JavaScript
- Docker

## Created by TCG TECH
