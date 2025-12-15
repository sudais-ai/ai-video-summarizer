import os
import json
import uuid
import re
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from openai import OpenAI
import yt_dlp
import nltk
from fpdf import FPDF
import tempfile
import logging

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ai-video-summarizer-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    histories = db.relationship('History', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    video_url = db.Column(db.String(1000))
    summary = db.Column(db.Text)
    quiz_data = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already registered'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already taken'}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'email': user.email}})
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'user': {'id': user.id, 'username': user.username, 'email': user.email}})
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/api/user', methods=['GET'])
def get_user():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': {'id': current_user.id, 'username': current_user.username, 'email': current_user.email}})
    return jsonify({'authenticated': False})

def extract_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en', 'hi', 'ur'],
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Untitled Video')
            duration = info.get('duration', 0)
            description = info.get('description', '')
            
            transcript = ""
            
            if 'subtitles' in info and info['subtitles']:
                for lang in ['en', 'hi', 'ur']:
                    if lang in info['subtitles']:
                        subs = info['subtitles'][lang]
                        if subs:
                            transcript = f"[Subtitles available in {lang}]"
                            break
            
            if 'automatic_captions' in info and info['automatic_captions']:
                for lang in ['en', 'hi', 'ur']:
                    if lang in info['automatic_captions']:
                        captions = info['automatic_captions'][lang]
                        if captions:
                            for cap in captions:
                                if cap.get('ext') == 'json3' or cap.get('ext') == 'vtt':
                                    transcript = f"[Auto-captions available in {lang}]"
                                    break
                            if transcript:
                                break
            
            content_for_summary = description if description else title
            
            return {
                'title': title,
                'duration': duration,
                'description': description,
                'transcript': transcript,
                'content': content_for_summary
            }
    except Exception as e:
        logger.error(f"Error extracting video info: {str(e)}")
        raise Exception(f"Could not process video: {str(e)}")

def generate_summary_with_ai(content, title):
    if not openai_client:
        return generate_simple_summary(content, title)
    
    try:
        prompt = f"""Analyze and summarize this video content comprehensively:

Title: {title}

Content/Description:
{content[:4000]}

Please provide:
1. A detailed summary (3-4 paragraphs)
2. Key points (bullet points)
3. Main topics covered
4. Important concepts to remember

Format your response as JSON with keys: summary, key_points (array), topics (array), concepts (array)"""

        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"AI summary error: {str(e)}")
        return generate_simple_summary(content, title)

def generate_simple_summary(content, title):
    sentences = content.split('.')[:10]
    summary = '. '.join([s.strip() for s in sentences if s.strip()])
    
    return {
        'summary': summary if summary else f"This video is about: {title}",
        'key_points': [title, "Please watch the video for detailed content"],
        'topics': [title.split()[0] if title else "Video"],
        'concepts': ["Main topic from the video"]
    }

def generate_quiz_with_ai(content, title, num_questions=5):
    if not openai_client:
        return generate_simple_quiz(title, num_questions)
    
    try:
        prompt = f"""Based on this video content, create {num_questions} quiz questions:

Title: {title}
Content: {content[:3000]}

Create multiple choice questions with 4 options each. Make them educational and test understanding of key concepts.

Format as JSON array with objects containing:
- question: the question text
- options: array of 4 options (A, B, C, D format)
- correct: the correct option letter (A, B, C, or D)
- explanation: brief explanation of the correct answer"""

        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        
        result = json.loads(response.choices[0].message.content)
        if 'questions' in result:
            return result['questions']
        elif isinstance(result, list):
            return result
        else:
            return generate_simple_quiz(title, num_questions)
    except Exception as e:
        logger.error(f"AI quiz error: {str(e)}")
        return generate_simple_quiz(title, num_questions)

def generate_simple_quiz(title, num_questions=5):
    questions = []
    for i in range(num_questions):
        questions.append({
            'question': f"Question {i+1} about {title}?",
            'options': ['A) Option 1', 'B) Option 2', 'C) Option 3', 'D) Option 4'],
            'correct': 'A',
            'explanation': 'This is a sample question. AI-generated questions require OpenAI API key.'
        })
    return questions

@app.route('/api/process_video', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_url = data.get('url', '').strip()
        
        if not video_url:
            return jsonify({'success': False, 'error': 'Please provide a video URL'}), 400
        
        video_info = extract_video_info(video_url)
        
        content = video_info['content'] or video_info['title']
        summary_data = generate_summary_with_ai(content, video_info['title'])
        
        quiz = generate_quiz_with_ai(content, video_info['title'], 5)
        
        if current_user.is_authenticated:
            history = History(
                user_id=current_user.id,
                title=video_info['title'],
                video_url=video_url,
                summary=json.dumps(summary_data),
                quiz_data=json.dumps(quiz)
            )
            db.session.add(history)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'title': video_info['title'],
            'duration': video_info['duration'],
            'summary': summary_data,
            'quiz': quiz
        })
    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Please enter a message'}), 400
        
        if not openai_client:
            return jsonify({'success': False, 'error': 'AI chat requires OpenAI API key'}), 400
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant. Be friendly, informative, and helpful. Answer questions clearly and concisely."},
                {"role": "user", "content": message}
            ],
            max_completion_tokens=1024
        )
        
        ai_response = response.choices[0].message.content
        
        if current_user.is_authenticated:
            chat_entry = ChatHistory(
                user_id=current_user.id,
                message=message,
                response=ai_response
            )
            db.session.add(chat_entry)
            db.session.commit()
        
        return jsonify({'success': True, 'response': ai_response})
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Please login to view history'}), 401
    
    histories = History.query.filter_by(user_id=current_user.id).order_by(History.created_at.desc()).limit(50).all()
    
    return jsonify({
        'success': True,
        'history': [{
            'id': h.id,
            'title': h.title,
            'video_url': h.video_url,
            'created_at': h.created_at.isoformat()
        } for h in histories]
    })

@app.route('/api/history/<int:history_id>', methods=['GET'])
def get_history_item(history_id):
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Please login'}), 401
    
    history = History.query.filter_by(id=history_id, user_id=current_user.id).first()
    if not history:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    return jsonify({
        'success': True,
        'item': {
            'id': history.id,
            'title': history.title,
            'video_url': history.video_url,
            'summary': json.loads(history.summary) if history.summary else None,
            'quiz': json.loads(history.quiz_data) if history.quiz_data else None,
            'created_at': history.created_at.isoformat()
        }
    })

@app.route('/api/download_pdf', methods=['POST'])
def download_pdf():
    try:
        data = request.json
        title = data.get('title', 'Summary')
        summary = data.get('summary', {})
        quiz = data.get('quiz', [])
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf.set_font('Helvetica', 'B', 20)
        pdf.cell(0, 10, 'AI Video Summary', ln=True, align='C')
        pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 14)
        safe_title = title.encode('latin-1', 'replace').decode('latin-1')
        pdf.cell(0, 10, safe_title[:80], ln=True)
        pdf.ln(5)
        
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Summary:', ln=True)
        pdf.set_font('Helvetica', '', 10)
        
        summary_text = summary.get('summary', '') if isinstance(summary, dict) else str(summary)
        safe_summary = summary_text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, safe_summary[:2000])
        pdf.ln(5)
        
        if isinstance(summary, dict) and 'key_points' in summary:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(0, 10, 'Key Points:', ln=True)
            pdf.set_font('Helvetica', '', 10)
            for point in summary['key_points'][:10]:
                safe_point = str(point).encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, f"* {safe_point[:200]}")
            pdf.ln(5)
        
        if quiz:
            pdf.add_page()
            pdf.set_font('Helvetica', 'B', 14)
            pdf.cell(0, 10, 'Quiz Questions:', ln=True)
            pdf.ln(3)
            
            for i, q in enumerate(quiz[:10], 1):
                pdf.set_font('Helvetica', 'B', 11)
                question_text = q.get('question', f'Question {i}')
                safe_q = question_text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 6, f"Q{i}: {safe_q[:300]}")
                
                pdf.set_font('Helvetica', '', 10)
                options = q.get('options', [])
                for opt in options[:4]:
                    safe_opt = str(opt).encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, f"   {safe_opt[:100]}")
                
                pdf.set_font('Helvetica', 'I', 9)
                correct = q.get('correct', 'A')
                pdf.cell(0, 5, f"   Correct: {correct}", ln=True)
                pdf.ln(3)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            pdf.output(f.name)
            f.seek(0)
            with open(f.name, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            os.unlink(f.name)
        
        import base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        
        return jsonify({
            'success': True,
            'pdf': pdf_base64,
            'filename': f"{title[:50].replace(' ', '_')}_summary.pdf"
        })
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
