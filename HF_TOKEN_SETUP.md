# HuggingFace Token Setup Guide

## 1. Get Your HuggingFace Token

1. Go to [HuggingFace](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "Luna Image Generator")
4. Select "Read" permissions
5. Copy the generated token

## 2. Set Up Environment Variable

### Option A: Terminal (Recommended)
```bash
export HF_TOKEN="your_token_here"
```

### Option B: .env File
Create a `.env` file in your project root:
```
HF_TOKEN=your_token_here
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Backend

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000
```

## 5. Update Frontend API URL

In your frontend, make sure the API_BASE_URL points to your FastAPI server:
```javascript
const API_BASE_URL = 'http://localhost:8000'  // or your server URL
```

## Security Notes

- Never commit your HF token to version control
- Use read-only permissions for image generation
- Keep your token private and secure
- Rotate tokens regularly for security

## Troubleshooting

If you get "No token provided" error:
1. Check that HF_TOKEN environment variable is set
2. Verify token is valid and not expired
3. Ensure .env file is in the correct directory

## FastAPI Auto Docs

Once running, visit: http://localhost:8000/docs
- Interactive API documentation
- Test endpoints directly
- View request/response formats
