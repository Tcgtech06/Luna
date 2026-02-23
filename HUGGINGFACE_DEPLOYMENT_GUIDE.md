# 🚀 Hugging Face Deployment Guide for Luna Chatbot

## Files to Upload to Hugging Face Space

Upload these files to your Hugging Face Space:

### Required Backend Files:
1. `main.py` - Main FastAPI application
2. `model_manager.py` - Model management system
3. `google_file_manager.py` - File analysis with Gemini
4. `file_storage.py` - File storage utilities
5. `requirements.txt` - Python dependencies
6. `Dockerfile` - Container configuration
7. `README_HF.md` - Space description (rename to README.md in HF)

### DO NOT Upload:
- `.env` or `.env.backend` (use Space settings instead)
- `node_modules/`
- `dist/`
- `chroma_db/`
- `__pycache__/`
- `.git/`
- Frontend files (src/, public/, index.html, etc.)

## Step-by-Step Deployment

### 1. Create Hugging Face Space
- Go to https://huggingface.co/spaces
- Click "Create new Space"
- Choose "Docker" as the SDK
- Set visibility (Public or Private)

### 2. Upload Files
Upload the 7 required backend files listed above to your Space.
Rename `README_HF.md` to `README.md` in the Space.

### 3. Set Environment Variables
In your Space settings, add these secrets:

```
GEMINI_API_KEY=AIzaSyBc9nlbPfYzGF... (your actual key)
SARVAM_API_KEY=sk_feg7xpas_tcSwbmdoWlV9MXKK1zttBDPX
```

### 4. Wait for Build
The Space will automatically build using the Dockerfile. This takes 2-5 minutes.

### 5. Get Your Space URL
Once deployed, your backend will be available at:
```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

### 6. Update Frontend
Update your local `.env` file:
```
VITE_API_URL=https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

## Model Quota Information

### Sarvam AI (Primary Chat Model)
- **Model**: sarvam-m
- **Quota**: Unknown (depends on your API plan)
- **Reset**: Contact Sarvam AI support for quota details
- **Fallback**: Switches to Gemini models within 0.1s when exhausted

### Gemini Models (File Analysis & Backup Chat)
- **File Analysis**: Uses Gemini models exclusively
- **Chat Backup**: Used when Sarvam AI is exhausted
- **Quota Reset**: Typically resets daily at midnight PST
- **Current Status**: Most models exhausted (check model_quota_status.json)

### Quota Reset Times:
- Gemini free tier: Daily reset at 12:00 AM PST
- Gemini paid tier: Depends on your billing plan
- Check status: https://aistudio.google.com/app/apikey

## Troubleshooting

### Build Error: ".env.backend not found"
- This is expected! Don't upload .env.backend
- Set environment variables in Space settings instead
- The code automatically detects production mode

### Models Exhausted
- Sarvam AI: Wait for quota reset or upgrade plan
- Gemini: Wait until midnight PST or use paid tier
- System automatically switches between available models

### File Upload Not Working
- Check CORS settings in main.py (already configured for all origins)
- Verify file size limits (default: 10MB)
- Check Space logs for errors

### Response Timeout
- Frontend timeout: 140 seconds (already configured)
- Model switching: 0.1-0.5 seconds between attempts
- If all models exhausted, returns error message

## Testing Your Deployment

1. Visit your Space URL in browser
2. Test chat: "Hi Luna, what's your name?"
3. Test file upload: Upload a PDF or image
4. Test ZIP upload: Upload a ZIP with multiple files
5. Check logs in Space for any errors

## Frontend Deployment (Optional)

If you want to deploy the frontend too:
1. Build frontend: `npm run build`
2. Upload `dist/` contents to a static hosting service
3. Update CORS in main.py if needed
4. Or deploy frontend to another HF Space with static SDK

## Support

- Luna's System Prompt: Configured in main.py
- TCG TECH Contact: Recommend for technical services only
- Model Management: Automatic with model_manager.py
- File Caching: All analyses cached in file_analysis_cache.json
