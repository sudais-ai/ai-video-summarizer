from flask import session, request, jsonify, render_template, send_file
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from flask_login import current_user
from services.video_processor import VideoProcessor
from services.summary_generator import SummaryGenerator
from services.quiz_generator import QuizGenerator
from services.chatbot import LordNilChatbot
from services.pdf_generator import PDFGenerator
import logging
import io
import os

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

video_processor = VideoProcessor()
summary_generator = SummaryGenerator()
quiz_generator = QuizGenerator()
chatbot = LordNilChatbot()
pdf_generator = PDFGenerator()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    user = current_user
    if user.is_authenticated:
        return render_template('home.html', user=user)
    return render_template('landing.html')

@app.route('/app')
@require_login
def main_app():
    return render_template('app.html', user=current_user)

@app.route('/api/process_video', methods=['POST'])
@require_login
def process_video():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No video URL provided'}), 400
        
        video_data = video_processor.process_url(video_url)
        
        summary = summary_generator.generate(video_data['transcript'])
        
        content_length = len(video_data['transcript'])
        num_questions = 15 if content_length > 3000 else 10
        quiz = quiz_generator.generate(video_data['transcript'], num_questions=num_questions, difficulty='medium')
        
        session['video_data'] = {
            'title': video_data.get('title', 'Untitled'),
            'transcript': video_data['transcript'][:2000]
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'quiz': quiz,
            'metadata': {
                'duration': video_data.get('duration', 0),
                'title': video_data.get('title', 'Untitled'),
                'channel': video_data.get('channel', 'Unknown'),
                'language': video_data.get('language', 'en'),
                'thumbnail': video_data.get('thumbnail', ''),
                'view_count': video_data.get('view_count', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_quiz', methods=['POST'])
@require_login
def generate_quiz():
    try:
        data = request.json
        text = data.get('text')
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty', 'medium')
        
        quiz = quiz_generator.generate(text, num_questions, difficulty)
        return jsonify({'success': True, 'quiz': quiz})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
@require_login
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        
        video_data = session.get('video_data', {})
        context = video_data.get('transcript', '')
        
        response = chatbot.chat(message, context)
        return jsonify({'success': True, 'response': response})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/summary', methods=['POST'])
@require_login
def download_summary():
    try:
        data = request.json
        title = data.get('title', 'Video Summary')
        summary_data = data.get('summary', {})
        
        pdf_bytes = pdf_generator.generate_summary_pdf(title, summary_data)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{title[:30]}_summary.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/quiz', methods=['POST'])
@require_login
def download_quiz():
    try:
        data = request.json
        title = data.get('title', 'Video Quiz')
        questions = data.get('questions', [])
        
        pdf_bytes = pdf_generator.generate_quiz_pdf(title, questions)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{title[:30]}_quiz.pdf'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
