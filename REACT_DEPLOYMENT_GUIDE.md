# Luna - React Frontend + FastAPI Backend Deployment Guide

## Architecture

- **Frontend**: React + Vite (deployed separately)
- **Backend**: FastAPI (deployed on Hugging Face Spaces)

## Quick Start - Local Development

### 1. Start Backend (Terminal 1)

```bash
# Install backend dependencies
pip install -r requirements_fastapi.txt

# Set API key
export GEMINI_API_KEY="your_api_key_here"

# Run backend
python main.py
```

Backend runs on: http://localhost:7860

### 2. Start Frontend (Terminal 2)

```bash
# Navigate to frontend
cd luna-frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

Frontend runs on: http://localhost:3000

## Deployment

### Backend Deployment (Hugging Face Spaces)

1. **Create Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `luna-backend`
   - SDK: **Docker**
   - Create Space

2. **Upload Backend Files**
   - `Dockerfile`
   - `main.py`
   - `requirements_fastapi.txt`
   - `README.md`

3. **Add API Key Secret**
   - Settings → Repository secrets
   - Name: `GEMINI_API_KEY`
   - Value: Your Gemini API key

4. **Get Backend URL**
   - After build completes, copy your Space URL
   - Example: `https://huggingface.co/spaces/YOUR_USERNAME/luna-backend`

### Frontend Deployment

#### Option 1: Vercel (Recommended)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd luna-frontend
   vercel
   ```

3. **Set Environment Variable**
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add: `VITE_API_URL` = Your Hugging Face backend URL

4. **Redeploy**
   ```bash
   vercel --prod
   ```

#### Option 2: Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build**
   ```bash
   cd luna-frontend
   npm run build
   ```

3. **Deploy**
   ```bash
   netlify deploy --prod --dir=dist
   ```

4. **Set Environment Variable**
   - Netlify dashboard → Site settings → Environment variables
   - Add: `VITE_API_URL` = Your backend URL

#### Option 3: GitHub Pages

1. **Update vite.config.js**
   ```javascript
   export default defineConfig({
     base: '/luna-frontend/',  // Your repo name
     // ... rest of config
   })
   ```

2. **Build**
   ```bash
   npm run build
   ```

3. **Deploy**
   - Push `dist/` folder to `gh-pages` branch
   - Or use GitHub Actions

## Environment Variables

### Backend (.env or Hugging Face Secrets)
```
GEMINI_API_KEY=your_api_key_here
```

### Frontend (.env)
```
# Local development
VITE_API_URL=http://localhost:7860

# Production
VITE_API_URL=https://huggingface.co/spaces/YOUR_USERNAME/luna-backend
```

## File Structure

```
Luna/
├── main.py                      # Backend API
├── requirements_fastapi.txt     # Backend dependencies
├── Dockerfile                   # Backend Docker config
├── README.md                    # Backend README
└── luna-frontend/               # Frontend folder
    ├── src/
    │   ├── App.jsx             # Main React component
    │   ├── App.css             # Styles
    │   ├── main.jsx            # Entry point
    │   └── index.css           # Global styles
    ├── index.html              # HTML template
    ├── vite.config.js          # Vite config
    ├── package.json            # Dependencies
    ├── .env                    # Environment variables
    └── README.md               # Frontend README
```

## Testing

### Test Backend
```bash
curl http://localhost:7860/health
```

### Test Frontend
1. Open http://localhost:3000
2. Send a test message
3. Check browser console for errors

## Troubleshooting

### CORS Errors
- Ensure backend CORS allows your frontend domain
- Check `main.py` CORS configuration

### API Connection Failed
1. Verify backend is running
2. Check `VITE_API_URL` in frontend `.env`
3. Test backend health endpoint

### Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear cache: `npm run build -- --force`

## Production Checklist

- [ ] Backend deployed on Hugging Face
- [ ] Backend API key added as secret
- [ ] Backend health check working
- [ ] Frontend built successfully
- [ ] Frontend environment variable set
- [ ] Frontend deployed
- [ ] Test chat functionality
- [ ] Test file upload
- [ ] Test theme toggle
- [ ] Test on mobile

## URLs

After deployment:

- **Backend**: `https://huggingface.co/spaces/YOUR_USERNAME/luna-backend`
- **Frontend**: `https://your-app.vercel.app` (or your chosen platform)

## Support

For issues:
1. Check browser console
2. Check backend logs on Hugging Face
3. Verify environment variables
4. Test API endpoints directly

---

Created by TCG TECH
