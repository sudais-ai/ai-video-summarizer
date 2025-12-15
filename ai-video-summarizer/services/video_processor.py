import yt_dlp
import os
import re
import requests

class VideoProcessor:
    def __init__(self):
        print("Video processor initialized")
    
    def process_url(self, url):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'en-US', 'en-GB', 'hi', 'auto'],
                'subtitlesformat': 'json3',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            
            duration = info.get('duration', 0)
            title = info.get('title', 'Unknown Title')
            description = info.get('description', '')
            channel = info.get('channel', info.get('uploader', 'Unknown'))
            thumbnail = info.get('thumbnail', '')
            
            transcript = self._extract_transcript(info)
            
            if not transcript or len(transcript) < 100:
                transcript = self._build_content_from_metadata(info)
            
            return {
                'transcript': transcript,
                'segments': [],
                'duration': duration,
                'title': title,
                'channel': channel,
                'language': info.get('language', 'en') or 'en',
                'thumbnail': thumbnail,
                'view_count': info.get('view_count', 0),
                'description': description[:500] if description else ''
            }
                
        except Exception as e:
            raise Exception(f"Error processing video URL: {str(e)}")
    
    def _extract_transcript(self, info):
        transcript_text = ""
        subtitles = info.get('subtitles', {})
        auto_captions = info.get('automatic_captions', {})
        all_subs = {**subtitles, **auto_captions}
        preferred_langs = ['en', 'en-US', 'en-GB', 'en-orig', 'hi']
        
        for lang in preferred_langs:
            if lang in all_subs:
                sub_data = all_subs[lang]
                if isinstance(sub_data, list):
                    for sub in sub_data:
                        if sub.get('ext') == 'json3' or sub.get('ext') == 'vtt':
                            transcript_text = self._parse_subtitle_url(sub.get('url', ''))
                            if transcript_text:
                                return transcript_text
        
        if all_subs:
            first_lang = list(all_subs.keys())[0]
            sub_data = all_subs[first_lang]
            if isinstance(sub_data, list) and sub_data:
                transcript_text = self._parse_subtitle_url(sub_data[0].get('url', ''))
        
        return transcript_text
    
    def _parse_subtitle_url(self, url):
        if not url:
            return ""
        try:
            response = requests.get(url, timeout=10)
            content = response.text
            text_parts = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('WEBVTT') and not '-->' in line:
                    if not re.match(r'^\d+$', line) and not re.match(r'^\d{2}:\d{2}', line):
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        clean_line = re.sub(r'\{[^}]+\}', '', clean_line)
                        if clean_line and len(clean_line) > 1:
                            text_parts.append(clean_line)
            
            return ' '.join(text_parts)
        except:
            return ""
    
    def _build_content_from_metadata(self, info):
        parts = []
        title = info.get('title', '')
        if title:
            parts.append(f"Video Title: {title}")
        
        channel = info.get('channel', info.get('uploader', ''))
        if channel:
            parts.append(f"Channel: {channel}")
        
        description = info.get('description', '')
        if description:
            clean_desc = description[:2000]
            clean_desc = re.sub(r'https?://\S+', '', clean_desc)
            clean_desc = re.sub(r'#\w+', '', clean_desc)
            parts.append(f"Description: {clean_desc}")
        
        tags = info.get('tags', [])
        if tags:
            parts.append(f"Topics covered: {', '.join(tags[:15])}")
        
        categories = info.get('categories', [])
        if categories:
            parts.append(f"Category: {', '.join(categories)}")
        
        chapters = info.get('chapters', [])
        if chapters:
            chapter_titles = [ch.get('title', '') for ch in chapters if ch.get('title')]
            if chapter_titles:
                parts.append(f"Chapters: {', '.join(chapter_titles)}")
        
        return '. '.join(parts)
