# Hugging Face Deployment Checklist

## Files to Upload

✅ Required files for deployment:

1. ✅ `Dockerfile` - Docker configuration
2. ✅ `main.py` - FastAPI backend
3. ✅ `requirements_fastapi.txt` - Python dependencies
4. ✅ `README.md` - Space description (with YAML frontmatter)
5. ✅ `static/index.html` - Frontend UI

## Step-by-Step Deployment

### 1. Create Space
- [ ] Go to https://huggingface.co/spaces
- [ ] Click "Create new Space"
- [ ] Name: `luna-chatbot` (or your choice)
- [ ] SDK: Select **Docker**
- [ ] Hardware: CPU basic (free)
- [ ] Click "Create Space"

### 2. Upload Files
- [ ] Upload `Dockerfile`
- [ ] Upload `main.py`
- [ ] Upload `requirements_fastapi.txt`
- [ ] Upload `README.md`
- [ ] Create folder `static`
- [ ] Upload `index.html` to `static/` folder

### 3. Configure Secrets
- [ ] Go to Settings tab
- [ ] Scroll to "Repository secrets"
- [ ] Click "New secret"
- [ ] Name: `GEMINI_API_KEY`
- [ ] Value: Your Google Gemini API key
- [ ] Click "Add"

### 4. Wait for Build
- [ ] Go to "App" tab
- [ ] Wait 2-5 minutes for build
- [ ] Check "Logs" if any errors

### 5. Test Your App
- [ ] Open the app URL
- [ ] Test sending a message
- [ ] Test file upload
- [ ] Test theme toggle

## Your Space URL

After deployment, your Luna chatbot will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/luna-chatbot
```

## Quick Commands (Git Method)

```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/luna-chatbot
cd luna-chatbot

# Copy files from Luna project
cp Dockerfile main.py requirements_fastapi.txt README.md .
cp -r static .

# Commit and push
git add .
git commit -m "Deploy Luna chatbot"
git push
```

## Troubleshooting

### Build Failed?
- Check Dockerfile syntax
- Verify all files are uploaded
- Check build logs in "Logs" tab

### App Not Loading?
- Verify GEMINI_API_KEY is set in secrets
- Check application logs
- Ensure port 7860 is used

### API Errors?
- Verify API key is valid
- Check Google Cloud quota
- Test API key locally first

## Post-Deployment

- [ ] Share your Space URL
- [ ] Update Space description
- [ ] Add screenshots to README
- [ ] Monitor usage in Space settings

---

**Need Help?** Check DEPLOYMENT_GUIDE.md for detailed instructions.

Created by TCG TECH
