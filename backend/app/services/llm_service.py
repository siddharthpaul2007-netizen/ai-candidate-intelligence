import json
import re
from typing import Optional, Dict, Any
from app.config import settings

class LLMService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Google GenAI Client: {e}")

    def generate_text(self, prompt: str, system_instruction: str = "") -> str:
        if self.client:
            try:
                model_name = "gemini-2.5-flash"
                contents = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini API call failed: {e}. Falling back...")
        return ""

    def generate_json(self, prompt: str, system_instruction: str = "") -> Optional[Dict[str, Any]]:
        raw_text = self.generate_text(prompt, system_instruction)
        if not raw_text:
            return None
        
        # Try to find JSON in markdown code blocks or raw string
        json_match = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", raw_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_str = raw_text.strip()
            
        try:
            return json.loads(json_str)
        except Exception as e:
            print(f"Failed to parse JSON from LLM output: {e}")
            return None

llm_service = LLMService()
