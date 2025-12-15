import os
import re
from typing import List, Dict
import google.generativeai as genai

class SummaryGenerator:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def generate(self, text: str, max_length: int = 500) -> Dict:
        try:
            if self.model and len(text) > 50:
                return self._generate_with_ai(text)
            else:
                return self._generate_fallback(text, max_length)
        except Exception as e:
            print(f"AI Summary error: {e}")
            return self._generate_fallback(text, max_length)
    
    def _generate_with_ai(self, text: str) -> Dict:
        prompt = f"""You are an expert educational content summarizer. Analyze this video lecture content and provide a comprehensive educational summary in simple English that students can easily understand.

VIDEO CONTENT:
{text[:12000]}

Please provide your response in this EXACT format:

## LECTURE OVERVIEW
Write a brief 2-3 sentence overview of what this lecture covers.

## MAIN TOPICS AND HEADINGS
List all the main topics/headings discussed in the lecture with brief descriptions.

## DETAILED EXPLANATIONS
For each key concept:
### [Concept Name]
**Definition:** Simple definition in basic English
**Explanation:** Detailed explanation with examples
**Key Points:** Important things to remember

## KEY TAKEAWAYS
- List 7-10 important points students should remember
- Each point should be a complete sentence

## EXAMPLES FROM THE LECTURE
List any examples, case studies, or demonstrations mentioned.

## FINAL SUMMARY
Write a comprehensive 150-200 word summary that captures all the essential information from the lecture. Make it clear and easy to understand.

Remember to:
- Use simple, basic English
- Explain technical terms clearly
- Include all important headings and topics
- Make it educational and helpful for students"""

        response = self.model.generate_content(prompt)
        content = response.text
        
        key_points = self._extract_key_points(content)
        
        return {
            'full_summary': content,
            'key_points': key_points,
            'word_count': len(content.split()),
            'ai_generated': True
        }
    
    def _extract_key_points(self, content: str) -> List[str]:
        points = []
        lines = content.split('\n')
        in_points = False
        
        for line in lines:
            if 'KEY TAKEAWAYS' in line.upper() or 'KEY POINTS' in line.upper():
                in_points = True
                continue
            if in_points and line.strip().startswith('-'):
                clean = line.strip().lstrip('-').strip()
                if len(clean) > 20:
                    points.append(clean)
            if in_points and ('##' in line or 'EXAMPLES' in line.upper() or 'SUMMARY' in line.upper()):
                in_points = False
        
        return points[:10]
    
    def _generate_fallback(self, text: str, max_length: int) -> Dict:
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
