import openai
from transformers import pipeline
import os
from typing import List, Dict
import json

class SummaryGenerator:
    def __init__(self):
        # Initialize with Hugging Face transformers as fallback
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # You can also use OpenAI API (uncomment and add your API key)
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        # self.use_openai = True if openai.api_key else False
    
    def generate(self, text: str, max_length: int = 200) -> Dict:
        """Generate summary from text"""
        try:
            # For longer texts, split into chunks
            chunks = self._split_text(text)
            summaries = []
            
            for chunk in chunks:
                # Use Hugging Face model
                summary = self.summarizer(
                    chunk,
                    max_length=max_length // len(chunks),
                    min_length=30,
                    do_sample=False
                )[0]['summary_text']
                summaries.append(summary)
            
            # Combine summaries
            final_summary = " ".join(summaries)
            
            # Extract key points
            key_points = self._extract_key_points(final_summary)
            
            return {
                'full_summary': final_summary,
                'key_points': key_points,
                'word_count': len(final_summary.split())
            }
            
        except Exception as e:
            # Fallback to simple extraction
            sentences = text.split('.')
            key_points = sentences[:5]  # First 5 sentences as summary
            return {
                'full_summary': ' '.join(key_points),
                'key_points': key_points,
                'word_count': len(' '.join(key_points).split())
            }
    
    def _split_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into manageable chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text"""
        sentences = text.split('.')
        return [s.strip() + '.' for s in sentences if len(s.strip()) > 20][:5]