# Quick Start - Luna Local Development

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

## Step 1: Start Backend

Open Terminal 1:

```bash
# Install Python dependencies
pip install -r requirements_fastapi.txt

# Set your Gemini API key
export GEMINI_API_KEY="AIzaSyBc9nlbPfYzGFIVeDz8hOcU61Ig4R7NxYc"

# Run backend server
python main.py
```

✅ Backend running at: http://localhost:7860

## Step 2: Start Frontend

Open Terminal 2:

```bash
# Navigate to frontend folder
cd luna-frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

## Step 3: Test Luna

1. Open browser: http://localhost:3000
2. You should see Luna's beautiful interface
3. Type a message and press Enter
4. Luna will respond!

## Features to Test

- ✅ Send messages
- ✅ Upload files (click 📎 button)
- ✅ Toggle theme (click 🌙 button)
- ✅ View typing indicator
- ✅ See message history

## Troubleshooting

### Backend won't start?
- Check if port 7860 is available
- Verify Python dependencies are installed
- Check API key is set

### Frontend won't start?
- Check if port 3000 is available
- Run `npm install` again
- Delete `node_modules` and reinstall

### Can't connect to backend?
- Ensure backend is running on port 7860
- Check `.env` file in `luna-frontend/` folder
- Verify `VITE_API_URL=http://localhost:7860`

### CORS errors?
- Backend CORS is configured for localhost:3000
- Check browser console for details

## Next Steps

Once everything works locally:

1. Deploy backend to Hugging Face (see REACT_DEPLOYMENT_GUIDE.md)
2. Deploy frontend to Vercel/Netlify
3. Update frontend `.env` with production backend URL

---

Created by TCG TECH
