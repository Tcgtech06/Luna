# ✅ Hugging Face Deployment Checklist

## Files to Upload (7 files total)
- [ ] main.py
- [ ] model_manager.py
- [ ] google_file_manager.py
- [ ] file_storage.py
- [ ] requirements.txt
- [ ] Dockerfile
- [ ] README_HF.md (rename to README.md in HF)

## Environment Variables to Set in Space Settings
- [ ] GEMINI_API_KEY
- [ ] SARVAM_API_KEY

## After Deployment
- [ ] Wait for build to complete (2-5 minutes)
- [ ] Copy your Space URL
- [ ] Update local `.env` file with: `VITE_API_URL=https://YOUR_SPACE_URL.hf.space`
- [ ] Test chat functionality
- [ ] Test file upload (PDF, image, ZIP)
- [ ] Verify model switching works

## Model Quota Status

### When will Sarvam AI exhaust?
- Depends on your API plan usage
- Check with Sarvam AI support for quota details
- System automatically switches to Gemini within 0.1s when exhausted

### When will Gemini quota reset?
- **Free Tier**: Daily at 12:00 AM PST (Pacific Standard Time)
- **Paid Tier**: Depends on your billing plan
- Check your quota: https://aistudio.google.com/app/apikey

### Current Model Status:
- Sarvam AI (sarvam-m): Active (primary chat model)
- Gemini Models: Most exhausted, waiting for reset
- File Analysis: Uses Gemini exclusively (cached to reduce quota usage)
- Chat Backup: Switches to available Gemini models when Sarvam exhausted

## Notes
- Don't upload .env.backend - use Space settings for secrets
- Frontend stays local or deploy separately
- All file analyses are cached in JSON for unlimited reuse
- Model switching happens automatically within 0.1-0.5 seconds
