# AI Video Summarizer

## Overview
An AI-powered video summarization and quiz generation application. Users can provide a YouTube URL and the system will extract information, generate summaries, and create quiz questions based on the video content.

## Project Structure
```
backend/
├── app.py              # Flask application entry point
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Simple status page
└── services/
    ├── video_processor.py     # Video URL processing with yt-dlp
    ├── summary_generator.py   # Text summarization
    └── quiz_generator.py      # Quiz question generation

frontend/               # Static frontend files (not currently used)
cpp-modules/           # C++ text analyzer (not currently used)
java-backend/          # Java video processor (not currently used)
```

## Running the Application
The application runs on port 5000 using Flask:
```bash
cd backend && python app.py
```

## API Endpoints
- `GET /` - Status page
- `POST /api/process_video` - Process a video URL and generate summary + quiz
- `POST /api/generate_quiz` - Generate quiz from text
- `POST /api/summarize` - Generate summary from text

## Dependencies
- Flask, Flask-CORS for web server
- yt-dlp for video metadata extraction
- nltk for text processing
- ffmpeg (system) for audio processing

## Notes
- The original project used heavy ML dependencies (whisper, transformers, torch) that were simplified for Replit compatibility
- Video processing extracts metadata and description from URLs rather than full transcription
