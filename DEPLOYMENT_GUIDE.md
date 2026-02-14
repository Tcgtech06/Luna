# Luna - Hugging Face Deployment Guide

## Prerequisites

1. A Hugging Face account (sign up at https://huggingface.co)
2. Your Google Gemini API key

## Deployment Steps

### Method 1: Using Hugging Face Web Interface (Recommended)

1. **Create a New Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Fill in the details:
     - Space name: `luna-chatbot` (or your preferred name)
     - License: MIT
     - Select SDK: **Docker**
     - Space hardware: CPU basic (free tier works fine)
   - Click "Create Space"

2. **Upload Files**
   - You'll be redirected to your new Space
   - Click "Files" tab
   - Upload these files:
     - `Dockerfile`
     - `main.py`
     - `requirements_fastapi.txt`
     - `README.md`
     - Create a folder named `static` and upload `index.html` inside it

3. **Add API Key as Secret**
   - Go to "Settings" tab
   - Scroll to "Repository secrets"
   - Click "New secret"
   - Name: `GEMINI_API_KEY`
   - Value: Your Google Gemini API key
   - Click "Add"

4. **Wait for Build**
   - Go back to "App" tab
   - The Space will automatically build (takes 2-5 minutes)
   - Once complete, your Luna chatbot will be live!

### Method 2: Using Git (Advanced)

1. **Clone Your Space Repository**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/luna-chatbot
   cd luna-chatbot
   ```

2. **Copy Files**
   ```bash
   # Copy from your Luna project
   cp /path/to/Luna/Dockerfile .
   cp /path/to/Luna/main.py .
   cp /path/to/Luna/requirements_fastapi.txt .
   cp /path/to/Luna/README.md .
   cp -r /path/to/Luna/static .
   ```

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "Deploy Luna chatbot"
   git push
   ```

4. **Add API Key**
   - Go to your Space settings on Hugging Face
   - Add `GEMINI_API_KEY` as a secret (see Method 1, step 3)

## File Structure

Your Hugging Face Space should have this structure:

```
luna-chatbot/
├── Dockerfile
├── main.py
├── requirements_fastapi.txt
├── README.md
└── static/
    └── index.html
```

## Troubleshooting

### Build Fails
- Check the build logs in the "Logs" tab
- Ensure all files are uploaded correctly
- Verify Dockerfile syntax

### App Doesn't Load
- Check if the build completed successfully
- Verify the API key is set correctly in secrets
- Check application logs for errors

### API Errors
- Verify your Gemini API key is valid
- Check if you have quota remaining on your Google Cloud account
- Ensure the key has the correct permissions

## Updating Your Space

To update your deployed app:

1. Make changes to your local files
2. Upload the changed files to your Space (via web or git)
3. The Space will automatically rebuild

## Custom Domain (Optional)

Hugging Face provides a default URL: `https://huggingface.co/spaces/YOUR_USERNAME/luna-chatbot`

For a custom domain, you'll need a Pro account.

## Support

- Hugging Face Docs: https://huggingface.co/docs/hub/spaces
- Docker SDK Guide: https://huggingface.co/docs/hub/spaces-sdks-docker

## Notes

- Free tier CPU is sufficient for Luna
- The app will sleep after 48 hours of inactivity (free tier)
- Upgrade to Pro for persistent hosting
- Build time: ~2-5 minutes
- Cold start time: ~10-30 seconds

---

Created by TCG TECH
