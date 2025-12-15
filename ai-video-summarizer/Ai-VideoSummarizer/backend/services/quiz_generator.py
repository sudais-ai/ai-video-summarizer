import random
import re
from typing import List, Dict
import json
from nltk.tokenize import sent_tokenize
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class QuizGenerator:
    def __init__(self):
        self.question_templates = {
            'mcq': [
                "What is the main idea about {topic}?",
                "According to the text, what is {concept}?",
                "Which of the following best describes {term}?",
                "What was mentioned about {topic}?"
            ],
            'true_false': [
                "{statement} - True or False?",
                "Is it true that {statement}?"
            ]
        }
    
    def generate(self, text: str, num_questions: int = 5, difficulty: str = 'medium') -> List[Dict]:
        """Generate quiz questions from text"""
        try:
            # Extract key terms and concepts
            key_terms = self._extract_key_terms(text)
            sentences = sent_tokenize(text)
            
            questions = []
            
            # Generate MCQ questions
            for i in range(min(num_questions, len(key_terms))):
                if i < len(key_terms):
                    term = key_terms[i]
                    question = self._generate_mcq(term, text, sentences, difficulty)
                    if question:
                        questions.append(question)
            
            # Generate True/False questions
            remaining = num_questions - len(questions)
            for i in range(min(remaining, len(sentences) // 2)):
                question = self._generate_true_false(sentences[i], sentences)
                if question:
                    questions.append(question)
            
            return questions
            
        except Exception as e:
            # Fallback to simple questions
            return self._generate_fallback_questions(text, num_questions)
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from text"""
        # Simple extraction based on capitalization and frequency
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        word_freq = {}
        
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most frequent terms
        sorted_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [term[0] for term in sorted_terms[:10]]
    
    def _generate_mcq(self, term: str, text: str, sentences: List[str], difficulty: str) -> Dict:
        """Generate multiple choice question"""
        try:
            # Find context for the term
            context_sentences = [s for s in sentences if term in s]
            if not context_sentences:
                return None
            
            context = context_sentences[0]
            template = random.choice(self.question_templates['mcq'])
            question_text = template.format(topic=term, concept=term, term=term)
            
            # Generate options
            correct_answer = self._extract_answer(context, term)
            
            # Generate distractors (wrong answers)
            distractors = self._generate_distractors(term, text, difficulty)
            
            # Ensure we have 4 options
            options = [correct_answer] + distractors[:3]
            random.shuffle(options)
            
            return {
                'type': 'mcq',
                'question': question_text,
                'options': options,
                'correct_answer': correct_answer,
                'explanation': context
            }
            
        except:
            return None
    
    def _generate_true_false(self, statement: str, all_sentences: List[str]) -> Dict:
        """Generate true/false question"""
        try:
            # Modify statement for about 50% true questions
            is_true = random.choice([True, False])
            
            if not is_true:
                # Make statement false by altering key words
                words = statement.split()
                if len(words) > 3:
                    idx = random.randint(0, len(words) - 1)
                    words[idx] = random.choice(['not', 'never', 'always', 'all', 'none'])
                    statement = ' '.join(words)
            
            template = random.choice(self.question_templates['true_false'])
            question_text = template.format(statement=statement)
            
            return {
                'type': 'true_false',
                'question': question_text,
                'options': ['True', 'False'],
                'correct_answer': 'True' if is_true else 'False',
                'explanation': "Based on the video content"
            }
            
        except:
            return None
    
    def _extract_answer(self, sentence: str, term: str) -> str:
        """Extract answer from sentence"""
        # Simple extraction - take the part after the term
        parts = sentence.split(term, 1)
        if len(parts) > 1:
            return parts[1].strip('. ,;').capitalize()
        return sentence
    
    def _generate_distractors(self, term: str, text: str, difficulty: str) -> List[str]:
        """Generate wrong answer options"""
        # Get other terms from text
        all_terms = self._extract_key_terms(text)
        other_terms = [t for t in all_terms if t != term][:10]
        
        distractors = []
        
        # Generate plausible distractors based on difficulty
        if difficulty == 'easy':
            distractors = [
                f"Not mentioned in the video",
                f"Completely different from {term}",
                f"Opposite of what was said"
            ]
        elif difficulty == 'medium':
            if other_terms:
                distractors = [
                    f"Related to {random.choice(other_terms)}",
                    f"Similar to {random.choice(other_terms)}",
                    f"Part of {random.choice(other_terms)}"
                ]
        else:  # hard
            distractors = [
                f"A common misconception about {term}",
                f"What people often think about {term}",
                f"Historical context of {term}"
            ]
        
        return distractors
    
    def _generate_fallback_questions(self, text: str, num_questions: int) -> List[Dict]:
        """Generate simple fallback questions"""
        sentences = sent_tokenize(text)
        questions = []
        
        for i in range(min(num_questions, len(sentences))):
            sentence = sentences[i]
            words = sentence.split()
            
            if len(words) > 5:
                # Create fill-in-the-blank
                blank_word = random.choice([w for w in words if len(w) > 3])
                question_text = sentence.replace(blank_word, "______")
                
                questions.append({
                    'type': 'fill_blank',
                    'question': question_text,
                    'options': [blank_word] + random.sample(words, 3),
                    'correct_answer': blank_word,
                    'explanation': sentence
                })
        
        return questions