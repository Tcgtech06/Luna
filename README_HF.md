---
title: Luna AI Chatbot Backend
emoji: 🌙
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# Luna AI Chatbot Backend

Luna is an emotionally intelligent AI assistant created by TCG TECH.

## Features

- 🤖 Dual AI Models: Sarvam AI (primary) + Gemini (backup)
- 📁 File Analysis: PDF, TXT, Images, ZIP files
- 💬 Emotional Intelligence: Adapts to user emotions
- 🌐 Multi-language: English, Tamil, Tanglish
- 💕 Relationship Mode: Life advice and emotional support

## Environment Variables

Set these in Hugging Face Spaces Settings:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `SARVAM_API_KEY`: Your Sarvam AI API key

## API Endpoints

- `POST /chat`: Chat with Luna
- `POST /upload`: Upload files
- `POST /analyze-file`: Analyze files with Gemini
- `GET /health`: Health check

## Created by TCG TECH

Visit: https://tcgtech.in
