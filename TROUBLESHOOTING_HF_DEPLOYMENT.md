# 🔧 Troubleshooting Hugging Face Deployment

## Current Error: ERR_CONNECTION_REFUSED

This means the backend isn't responding. Here's how to fix it:

## Step 1: Check Space Status
1. Go to https://huggingface.co/spaces/tcgtech/luna-chatbot
2. Look at the top - is it showing "Building" or "Running"?
3. Click on "Logs" tab to see what's happening

## Step 2: Set Environment Variables (CRITICAL!)
The Space WILL NOT START without these:

1. Go to your Space settings: https://huggingface.co/spaces/tcgtech/luna-chatbot/settings
2. Scroll to "Repository secrets"
3. Add these two secrets:

```
Name: GEMINI_API_KEY
Value: [Your actual Gemini API key]

Name: SARVAM_API_KEY  
Value: sk_feg7xpas_tcSwbmdoWlV9MXKK1zttBDPX
```

4. Click "Save" after adding each one
5. The Space will automatically restart

## Step 3: Check Build Logs
In the Logs tab, look for:

### Good Signs:
```
✅ Google File Manager initialized for file analysis
Starting Luna chatbot server...
INFO: Uvicorn running on http://0.0.0.0:7860
INFO: Application startup complete
```

### Bad Signs:
```
SyntaxError: ...
ModuleNotFoundError: ...
KeyError: ...
```

## Step 4: Test the Backend Directly
Once the Space shows "Running", test it:

1. Open: https://tcgtech-luna-chatbot.hf.space/
2. You should see: `{"message":"Luna Chatbot API is running"}`
3. If you see this, backend is working!

## Step 5: Update Frontend URL
Make sure your Netlify deployment has the correct backend URL.

### For Local Testing:
In `.env`:
```
VITE_API_URL=https://tcgtech-luna-chatbot.hf.space
```

### For Netlify Deployment:
In Netlify dashboard → Site settings → Environment variables:
```
VITE_API_URL=https://tcgtech-luna-chatbot.hf.space
```

Then redeploy the frontend.

## Common Issues & Solutions

### Issue 1: Space keeps restarting
**Cause**: Missing environment variables or syntax error
**Solution**: 
- Check you added both GEMINI_API_KEY and SARVAM_API_KEY
- Look at logs for error messages
- Verify main.py has no syntax errors

### Issue 2: "Application startup failed"
**Cause**: Missing dependencies or import errors
**Solution**:
- Check requirements.txt includes all packages
- Verify all 4 Python files are uploaded (main.py, model_manager.py, google_file_manager.py, file_storage.py)

### Issue 3: CORS errors in browser
**Cause**: Frontend trying to connect from different domain
**Solution**: Already fixed - CORS allows all origins in main.py

### Issue 4: Timeout errors
**Cause**: Models taking too long or all exhausted
**Solution**: 
- Frontend timeout is 140 seconds (already configured)
- Wait for Gemini quota to reset (midnight PST)
- Sarvam AI should respond within seconds

## Verification Checklist

- [ ] Space shows "Running" status (not "Building" or "Error")
- [ ] Both environment variables are set in Space settings
- [ ] Can access https://tcgtech-luna-chatbot.hf.space/ and see API message
- [ ] Frontend .env or Netlify env vars point to HF Space URL
- [ ] Frontend redeployed after changing environment variables
- [ ] Browser console shows requests going to HF Space (not localhost)

## Quick Test Commands

### Test backend health:
```bash
curl https://tcgtech-luna-chatbot.hf.space/
```

Expected response:
```json
{"message":"Luna Chatbot API is running"}
```

### Test chat endpoint:
```bash
curl -X POST https://tcgtech-luna-chatbot.hf.space/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hi","mode":"normal","history":[]}'
```

Should return Luna's response.

## Still Not Working?

1. Check Space logs for specific error messages
2. Verify API keys are valid (test them locally first)
3. Make sure you uploaded the corrected main.py (without syntax errors)
4. Try restarting the Space manually from settings
5. Check if Hugging Face Spaces is having issues: https://status.huggingface.co/

## Contact Info
If backend works but you need help with frontend:
- Check browser console for exact error
- Verify network tab shows requests to correct URL
- Make sure Netlify build includes updated .env values
