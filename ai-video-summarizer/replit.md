# AI Video Summarizer

## Overview
An AI-powered web application that transforms YouTube video lectures into comprehensive summaries and interactive quizzes. Features user authentication, a chatbot assistant (LORD NIL), and PDF downloads.

## Features
- **Video Summarization**: Paste a YouTube link to get detailed summaries with headings, definitions, and examples
- **Quiz Generation**: Auto-generated quizzes with 10-20 questions covering all topics
- **LORD NIL Chatbot**: AI assistant powered by Google Gemini for learning help
- **PDF Downloads**: Export summaries and quizzes as PDF documents
- **User Authentication**: Login with Google, GitHub, or email via Replit Auth

## Tech Stack
- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **AI**: Google Gemini API
- **Video Processing**: yt-dlp
- **Authentication**: Replit Auth (OpenID Connect)
- **PDF Generation**: ReportLab

## Project Structure
```
/
├── app.py              # Flask app initialization
├── main.py             # Entry point
├── routes.py           # API routes
├── models.py           # Database models
├── replit_auth.py      # Authentication logic
├── services/           # Business logic
│   ├── video_processor.py
│   ├── summary_generator.py
│   ├── quiz_generator.py
│   ├── chatbot.py
│   └── pdf_generator.py
├── templates/          # HTML templates
│   ├── landing.html
│   ├── home.html
│   ├── app.html
│   └── error.html
└── static/             # CSS and JS
    ├── css/styles.css
    └── js/
        ├── landing.js
        └── app.js
```

## Environment Variables
- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string (auto-set)
- `SESSION_SECRET` - Session encryption key

## Running the App
The app runs on port 5000. Access the landing page to login, then use the main app to analyze videos.

## Recent Changes
- December 2024: Complete rebuild with authentication, Gemini integration, and enhanced UI
