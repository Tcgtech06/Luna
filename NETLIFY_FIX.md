# 🔧 Fix Netlify Deployment

## Problem
Your Netlify frontend is still trying to connect to `localhost:7860` instead of the Hugging Face Space.

## Solution

### Step 1: Verify Environment Variable in Netlify
1. Go to Netlify Dashboard → Your Site → Site settings → Environment variables
2. Make sure you have:
   ```
   Key: VITE_API_URL
   Value: https://tcgtech-luna-chatbot.hf.space
   ```
3. **IMPORTANT**: The key MUST be `VITE_API_URL` (not `API_URL` or anything else)

### Step 2: Trigger a New Deploy
After adding/updating the environment variable:
1. Go to Deploys tab
2. Click "Trigger deploy" → "Clear cache and deploy site"
3. Wait for build to complete

### Step 3: Verify the Build
Check the deploy logs to confirm the environment variable is being used:
- Look for: "VITE_API_URL=https://tcgtech-luna-chatbot.hf.space"

### Step 4: Test
1. Open your Netlify site
2. Open browser console (F12)
3. Try sending a message
4. Check Network tab - requests should go to `https://tcgtech-luna-chatbot.hf.space/chat`
5. NOT to `localhost:7860/chat`

## Alternative: Manual Build and Deploy

If environment variables aren't working, you can build locally:

1. Update your local `.env` file:
   ```
   VITE_API_URL=https://tcgtech-luna-chatbot.hf.space
   ```

2. Build the project:
   ```bash
   npm run build
   ```

3. Deploy the `dist` folder to Netlify:
   - Drag and drop the `dist` folder to Netlify
   - Or use Netlify CLI: `netlify deploy --prod --dir=dist`

## Verify It's Working

### Check 1: Backend is running
Open: https://tcgtech-luna-chatbot.hf.space/
Should see: `{"message":"Luna Chatbot API is running"}`

### Check 2: Frontend connects to correct URL
1. Open your Netlify site
2. Open browser DevTools (F12) → Console tab
3. Send a message "hi"
4. Go to Network tab
5. Look for POST request to `/chat`
6. The URL should be: `https://tcgtech-luna-chatbot.hf.space/chat`
7. NOT: `http://localhost:7860/chat`

## Common Issues

### Issue: Still connecting to localhost
**Cause**: Environment variable not set correctly or build not refreshed
**Solution**: 
- Clear Netlify cache and redeploy
- Or build locally with correct .env and upload dist folder

### Issue: CORS error
**Cause**: Backend not allowing requests from Netlify domain
**Solution**: Already fixed - backend allows all origins

### Issue: Timeout
**Cause**: Models taking too long
**Solution**: Frontend timeout is 140 seconds, should be enough

## Quick Test Command

Test if backend is accessible:
```bash
curl -X POST https://tcgtech-luna-chatbot.hf.space/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hi","mode":"normal","history":[]}'
```

Should return Luna's response in JSON format.
