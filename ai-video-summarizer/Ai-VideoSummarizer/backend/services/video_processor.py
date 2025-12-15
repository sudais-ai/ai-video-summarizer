import whisper
import yt_dlp
import os
from moviepy.editor import VideoFileClip
import tempfile
import json

class VideoProcessor:
    def __init__(self):
        # Load Whisper model (choose based on your needs: tiny, base, small, medium, large)
        self.model = whisper.load_model("base")
        print("Whisper model loaded successfully")
    
    def process_url(self, url):
        """Process video from URL (YouTube, Vimeo, etc.)"""
        try:
            # Download audio from video
            with tempfile.TemporaryDirectory() as tmpdir:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(tmpdir, 'audio.%(ext)s'),
                    'quiet': True,
                    'no_warnings': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    audio_path = ydl.prepare_filename(info)
                
                # Transcribe audio
                result = self.model.transcribe(audio_path)
                
                # Get video metadata
                duration = info.get('duration', 0)
                title = info.get('title', 'Unknown Title')
                
                return {
                    'transcript': result['text'],
                    'segments': result.get('segments', []),
                    'duration': duration,
                    'title': title,
                    'language': result.get('language', 'en')
                }
                
        except Exception as e:
            raise Exception(f"Error processing video URL: {str(e)}")
    
    def process_local_video(self, filepath):
        """Process local video file"""
        try:
            # Extract audio from video
            video = VideoFileClip(filepath)
            audio_path = filepath + '.mp3'
            video.audio.write_audiofile(audio_path)
            
            # Transcribe audio
            result = self.model.transcribe(audio_path)
            
            # Clean up
            os.remove(audio_path)
            
            return {
                'transcript': result['text'],
                'segments': result.get('segments', []),
                'duration': video.duration,
                'title': os.path.basename(filepath),
                'language': result.get('language', 'en')
            }
            
        except Exception as e:
            raise Exception(f"Error processing local video: {str(e)}")