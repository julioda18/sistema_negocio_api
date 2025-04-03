import requests
from django.conf import settings

class DeepSeekService:
    def __init__(self, model='deepseek-chat', temperature=0.7, max_tokens=2000):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate_report(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Error al generar reporte: {str(e)}"