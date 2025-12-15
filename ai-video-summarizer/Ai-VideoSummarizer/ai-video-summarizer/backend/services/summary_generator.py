import os
import re
from typing import List, Dict
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

class SummaryGenerator:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    def generate(self, text: str, max_length: int = 500) -> Dict:
        """Generate AI-powered summary from text"""
        try:
            if self.client and len(text) > 50:
                return self._generate_with_ai(text)
            else:
                return self._generate_fallback(text, max_length)
        except Exception as e:
            print(f"AI Summary error: {e}")
            return self._generate_fallback(text, max_length)
    
    def _generate_with_ai(self, text: str) -> Dict:
        """Generate summary using OpenAI GPT"""
        prompt = f"""Analyze this video content and provide a comprehensive educational summary.

VIDEO CONTENT:
{text[:8000]}

Provide a response in this exact format:
1. MAIN SUMMARY: Write a clear, detailed paragraph (100-150 words) explaining the main concepts and ideas.

2. KEY POINTS: List exactly 5-7 important points that students should remember. Each point should be a complete sentence.

3. CONCEPTS EXPLAINED: Identify and briefly explain 3 key concepts or terms from the content.

Make the summary educational, clear, and helpful for students who want to understand this content deeply."""

        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content summarizer. Your summaries help students understand complex topics clearly. Always provide detailed, accurate, and helpful information."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=1500
        )
        
        content = response.choices[0].message.content
        
        key_points = self._extract_key_points(content)
        full_summary = self._extract_main_summary(content)
        
        return {
            'full_summary': full_summary,
            'key_points': key_points,
            'word_count': len(full_summary.split()),
            'ai_generated': True
        }
    
    def _extract_main_summary(self, content: str) -> str:
        """Extract main summary from AI response"""
        lines = content.split('\n')
        summary_lines = []
        in_summary = False
        
        for line in lines:
            if 'MAIN SUMMARY' in line.upper():
                in_summary = True
                continue
            if 'KEY POINTS' in line.upper() or 'CONCEPTS' in line.upper():
                in_summary = False
            if in_summary and line.strip():
                summary_lines.append(line.strip())
        
        if summary_lines:
            return ' '.join(summary_lines)
        
        for line in lines:
            if len(line.strip()) > 100:
                return line.strip()
        
        return content[:500]
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from AI response"""
        points = []
        lines = content.split('\n')
        in_points = False
        
        for line in lines:
            if 'KEY POINTS' in line.upper():
                in_points = True
                continue
            if 'CONCEPTS' in line.upper():
                in_points = False
            
            if in_points and line.strip():
                clean = re.sub(r'^[\d\-\*\.\)]+\s*', '', line.strip())
                if len(clean) > 20:
                    points.append(clean)
        
        if not points:
            for line in lines:
                clean = re.sub(r'^[\d\-\*\.\)]+\s*', '', line.strip())
                if len(clean) > 30 and len(clean) < 200:
                    points.append(clean)
                if len(points) >= 7:
                    break
        
        return points[:7]
    
    def _generate_fallback(self, text: str, max_length: int) -> Dict:
        """Fallback summary without AI"""
        text = self._clean_text(text)
        sentences = self._split_into_sentences(text)
        important = self._rank_sentences(sentences)
        
        key_points = []
        for s in important[:7]:
            if len(s) > 30:
                clean = s.strip()
                if not clean.endswith('.'):
                    clean += '.'
                key_points.append(clean)
        
        if not key_points:
            key_points = [text[:200] + '...'] if len(text) > 200 else [text]
        
        full_summary = ' '.join(key_points[:5])
        
        return {
            'full_summary': full_summary,
            'key_points': key_points,
            'word_count': len(full_summary.split()),
            'ai_generated': False
        }
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'#\w+', '', text)
        text = re.sub(r'\n+', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    def _rank_sentences(self, sentences: List[str]) -> List[str]:
        keywords = ['important', 'key', 'main', 'learn', 'understand', 'concept', 
                   'explain', 'demonstrate', 'topic', 'video', 'title', 'content']
        
        scored = []
        for i, sentence in enumerate(sentences):
            score = sum(2 for kw in keywords if kw in sentence.lower())
            if i < 3:
                score += 3
            if 10 <= len(sentence.split()) <= 40:
                score += 2
            scored.append((score, sentence))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored]
