import os
import google.generativeai as genai

class LordNilChatbot:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        
        self.system_prompt = """You are LORD NIL, a helpful and friendly AI assistant integrated into an educational video summarizer platform. 

Your personality:
- Friendly, helpful, and encouraging
- You speak in simple, clear English
- You're knowledgeable about education, learning, and studying
- You can help with questions about videos, summaries, quizzes, and general learning

When users ask about the platform:
- This platform helps summarize YouTube videos and create quizzes
- It uses AI to generate educational content
- Users can download summaries and quizzes as PDFs

Always be respectful and supportive. Help users learn effectively!"""
    
    def chat(self, message: str, context: str = None) -> str:
        if not self.model:
            return "I'm sorry, I'm not available right now. Please check if the API key is configured correctly."
        
        try:
            prompt = self.system_prompt + "\n\n"
            
            if context:
                prompt += f"Current video context:\n{context[:2000]}\n\n"
            
            prompt += f"User message: {message}\n\nLORD NIL response:"
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
