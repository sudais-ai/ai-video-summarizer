import os
import re
import json
from typing import List, Dict
import google.generativeai as genai

class QuizGenerator:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
    
    def generate(self, text: str, num_questions: int = 10, difficulty: str = 'medium') -> List[Dict]:
        try:
            if self.model and len(text) > 50:
                return self._generate_with_ai(text, num_questions, difficulty)
            else:
                return self._generate_fallback(text, num_questions)
        except Exception as e:
            print(f"AI Quiz error: {e}")
            return self._generate_fallback(text, num_questions)
    
    def _generate_with_ai(self, text: str, num_questions: int, difficulty: str) -> List[Dict]:
        content_length = len(text)
        if content_length > 5000:
            num_questions = min(20, max(num_questions, 15))
        elif content_length > 2000:
            num_questions = min(15, max(num_questions, 10))
        else:
            num_questions = max(num_questions, 8)
        
        prompt = f"""Based on this educational content, create {num_questions} quiz questions to test understanding. Create as many questions as possible to cover all the topics.

CONTENT:
{text[:10000]}

DIFFICULTY: {difficulty}

Create exactly {num_questions} multiple-choice questions. Make sure to:
1. Cover ALL topics mentioned in the content
2. Test important concepts, definitions, and examples
3. Have 4 answer options (A, B, C, D) for each question
4. Have exactly one correct answer
5. Include a brief explanation for the correct answer
6. Use simple English that students can understand

Respond ONLY with valid JSON in this exact format (no markdown, no code blocks):
{{
  "questions": [
    {{
      "question": "What is the main concept discussed?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "This is correct because..."
    }}
  ]
}}"""

        response = self.model.generate_content(prompt)
        content = response.text
        
        content = content.strip()
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                return self._generate_fallback(text, num_questions)
        
        questions = data.get('questions', [])
        
        formatted_questions = []
        for i, q in enumerate(questions):
            options = q.get('options', [])
            if len(options) >= 4:
                formatted_questions.append({
                    'id': i + 1,
                    'type': 'mcq',
                    'question': q.get('question', ''),
                    'options': options[:4],
                    'correct_answer': q.get('correct_answer', options[0]),
                    'explanation': q.get('explanation', 'This is the correct answer based on the content.')
                })
        
        return formatted_questions if formatted_questions else self._generate_fallback(text, num_questions)
    
    def _generate_fallback(self, text: str, num_questions: int) -> List[Dict]:
        questions = []
        sentences = self._split_sentences(text)
        key_terms = self._extract_key_terms(text)
        
        for i in range(min(num_questions, len(key_terms))):
            term = key_terms[i]
            context = [s for s in sentences if term.lower() in s.lower()]
            
            if context:
                question = {
                    'id': i + 1,
                    'type': 'mcq',
                    'question': f"What is discussed about '{term}' in the video?",
                    'options': [
                        f"It is a key concept explained in detail",
                        f"It is mentioned briefly",
                        f"It is not related to the main topic",
                        f"It contradicts the main idea"
                    ],
                    'correct_answer': "It is a key concept explained in detail",
                    'explanation': context[0][:200] if context else f"This concept was discussed in the video."
                }
                questions.append(question)
        
        return questions[:num_questions]
    
    def _split_sentences(self, text: str) -> List[str]:
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    def _extract_key_terms(self, text: str) -> List[str]:
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        word_freq = {}
        for word in words:
            if len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        sorted_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [term[0] for term in sorted_terms[:15]]
