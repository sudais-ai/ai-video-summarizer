import os
import re
import json
import random
from typing import List, Dict
from openai import OpenAI

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user

class QuizGenerator:
    def __init__(self):
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
    
    def generate(self, text: str, num_questions: int = 5, difficulty: str = 'medium') -> List[Dict]:
        """Generate AI-powered quiz questions from text"""
        try:
            if self.client and len(text) > 50:
                return self._generate_with_ai(text, num_questions, difficulty)
            else:
                return self._generate_fallback(text, num_questions)
        except Exception as e:
            print(f"AI Quiz error: {e}")
            return self._generate_fallback(text, num_questions)
    
    def _generate_with_ai(self, text: str, num_questions: int, difficulty: str) -> List[Dict]:
        """Generate quiz using OpenAI GPT"""
        prompt = f"""Based on this educational content, create {num_questions} quiz questions to test understanding.

CONTENT:
{text[:6000]}

DIFFICULTY: {difficulty}

Create exactly {num_questions} multiple-choice questions. Each question should:
1. Test important concepts from the content
2. Have 4 answer options (A, B, C, D)
3. Have exactly one correct answer
4. Include a brief explanation for the correct answer

Respond in this JSON format:
{{
  "questions": [
    {{
      "question": "What is the main concept discussed?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A",
      "explanation": "This is correct because..."
    }}
  ]
}}

Make questions educational and help reinforce learning."""

        response = self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert quiz creator for educational content. Create clear, educational multiple-choice questions that test understanding. Always respond with valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2000
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        questions = data.get('questions', [])
        
        formatted_questions = []
        for q in questions:
            options = q.get('options', [])
            if len(options) >= 4:
                formatted_questions.append({
                    'type': 'mcq',
                    'question': q.get('question', ''),
                    'options': options[:4],
                    'correct_answer': q.get('correct_answer', options[0]),
                    'explanation': q.get('explanation', 'This is the correct answer based on the video content.')
                })
        
        return formatted_questions if formatted_questions else self._generate_fallback(text, num_questions)
    
    def _generate_fallback(self, text: str, num_questions: int) -> List[Dict]:
        """Generate basic quiz without AI"""
        questions = []
        sentences = self._split_sentences(text)
        key_terms = self._extract_key_terms(text)
        
        for i in range(min(num_questions, len(key_terms))):
            term = key_terms[i]
            context = [s for s in sentences if term.lower() in s.lower()]
            
            if context:
                question = {
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
        
        remaining = num_questions - len(questions)
        for i in range(min(remaining, len(sentences))):
            if sentences[i] and len(sentences[i]) > 30:
                questions.append({
                    'type': 'true_false',
                    'question': f"True or False: {sentences[i][:150]}",
                    'options': ['True', 'False'],
                    'correct_answer': 'True',
                    'explanation': 'This statement is based on the video content.'
                })
        
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
        return [term[0] for term in sorted_terms[:10]]
