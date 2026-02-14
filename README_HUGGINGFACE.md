# Luna - AI Chatbot by TCG TECH

Luna is an intelligent AI chatbot powered by Google Gemini AI, built with FastAPI for deployment on Hugging Face Spaces.

## Features

- 🌙 Modern, responsive UI with glassmorphism design
- 💬 Real-time chat with typing indicators
- 📎 Integrated file and image upload
- 🔄 Automatic model fallback for reliability
- 🎨 Beautiful gradient design with dark/light theme

## Quick Start - Local Development

```bash
# Install dependencies
pip install -r requirements_fastapi.txt

# Set your API key
export GEMINI_API_KEY="your_api_key_here"

# Run the server
python main.py
```

Visit http://localhost:7860

## Deployment on Hugging Face

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

### Quick Deploy Steps:

1. Create a new Space on Hugging Face (SDK: Docker)
2. Upload: `Dockerfile`, `main.py`, `requirements_fastapi.txt`, `README.md`, and `static/` folder
3. Add secret: `GEMINI_API_KEY` = your_api_key
4. Wait for build to complete
5. Done! Your Luna chatbot is live

## File Structure

```
Luna/
├── Dockerfile              # Docker configuration for Hugging Face
├── main.py                 # FastAPI backend
├── requirements_fastapi.txt # Python dependencies
├── README.md               # This file
├── DEPLOYMENT_GUIDE.md     # Detailed deployment instructions
└── static/
    └── index.html          # Frontend UI
```

## API Endpoints

- `GET /`: Main chat interface
- `POST /chat`: Send message and get response
- `POST /upload`: Upload files

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)

## Tech Stack

- **Backend**: FastAPI, Python 3.10
- **AI**: Google Gemini AI via LangChain
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker on Hugging Face Spaces

## Features in Detail

### Chat Interface
- Clean, modern design with glassmorphism effects
- Smooth animations and transitions
- Typing indicators
- Message history

### File Upload
- Support for images (PNG, JPG, JPEG, GIF, BMP)
- Support for documents (PDF, TXT, DOC, DOCX, CSV, XLSX)
- Multiple file upload
- File preview badges

### Theme Toggle
- Dark mode (default)
- Light mode
- Smooth transitions

### AI Features
- Multiple Gemini model support
- Automatic fallback if one model fails
- Context-aware responses
- File-aware conversations

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

## License

MIT License - Created by TCG TECH

## Support

For issues or questions, please open an issue on the repository.

---

**Powered by Google Gemini AI | Built with ❤️ by TCG TECH**

