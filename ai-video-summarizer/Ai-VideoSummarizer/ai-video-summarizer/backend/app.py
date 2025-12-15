from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import uuid
from services.video_processor import VideoProcessor
from services.summary_generator import SummaryGenerator
from services.quiz_generator import QuizGenerator
import logging

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

video_processor = VideoProcessor()
summary_generator = SummaryGenerator()
quiz_generator = QuizGenerator()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/process_video', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_url = data.get('url')
        
        if not video_url:
            return jsonify({'error': 'No video URL provided'}), 400
        
        video_data = video_processor.process_url(video_url)
        
        summary = summary_generator.generate(video_data['transcript'])
        
        quiz = quiz_generator.generate(video_data['transcript'], num_questions=5, difficulty='medium')
        
        return jsonify({
            'success': True,
            'summary': summary,
            'quiz': quiz,
            'metadata': {
                'duration': video_data.get('duration', 0),
                'title': video_data.get('title', 'Untitled'),
                'language': video_data.get('language', 'en')
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.json
        text = data.get('text')
        num_questions = data.get('num_questions', 5)
        difficulty = data.get('difficulty', 'medium')
        
        quiz = quiz_generator.generate(text, num_questions, difficulty)
        return jsonify({'success': True, 'quiz': quiz})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        text = data.get('text')
        max_length = data.get('max_length', 200)
        
        summary = summary_generator.generate(text, max_length)
        return jsonify({'success': True, 'summary': summary})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
