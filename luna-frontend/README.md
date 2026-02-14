# Luna Frontend - React + Vite

Professional React frontend for Luna AI Chatbot.

## Features

- ⚡ Built with React 18 and Vite
- 🎨 Modern, professional UI with glassmorphism
- 🌙 Dark/Light theme toggle
- 📎 File upload support
- 💬 Real-time chat interface
- 📱 Fully responsive design
- 🚀 Fast and optimized

## Setup

### 1. Install Dependencies

```bash
cd luna-frontend
npm install
```

### 2. Configure Backend URL

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and set your backend URL:

```env
# For local development
VITE_API_URL=http://localhost:7860

# For production (Hugging Face)
VITE_API_URL=https://huggingface.co/spaces/YOUR_USERNAME/luna-backend
```

### 3. Run Development Server

```bash
npm run dev
```

Visit http://localhost:3000

## Build for Production

```bash
npm run build
```

The build output will be in the `dist/` folder.

## Deploy

### Option 1: Vercel

```bash
npm install -g vercel
vercel
```

### Option 2: Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod
```

### Option 3: GitHub Pages

1. Update `vite.config.js` with base path
2. Run `npm run build`
3. Deploy `dist/` folder to GitHub Pages

## Environment Variables

- `VITE_API_URL`: Backend API URL (required)

## Project Structure

```
luna-frontend/
├── src/
│   ├── App.jsx          # Main component
│   ├── App.css          # Styles
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── package.json         # Dependencies
└── .env                 # Environment variables
```

## Tech Stack

- React 18
- Vite
- Axios (HTTP client)
- Lucide React (Icons)

## Backend Integration

The frontend connects to the FastAPI backend deployed on Hugging Face Spaces.

### API Endpoints Used:

- `POST /chat` - Send messages
- `POST /upload` - Upload files

## Customization

### Change Theme Colors

Edit `App.css` and modify the gradient colors:

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change API URL

Update `.env` file with your backend URL.

## Troubleshooting

### CORS Errors

Make sure your backend has CORS enabled for your frontend domain.

### API Connection Failed

1. Check if backend is running
2. Verify `VITE_API_URL` in `.env`
3. Check browser console for errors

## Created by TCG TECH

Powered by React + Vite
