"""ChatGPT API client for generating email responses."""
import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI

from utils.logging_config import get_logger

# Import app configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.app_config import (
    CHATGPT_MODEL, CHATGPT_TEMPERATURE, CHATGPT_MAX_TOKENS,
    CHATGPT_SYSTEM_PROMPT, ZOOM_CONFIRMATION_KEYWORDS, EMAIL_SIGNATURE
)

# Module logger
logger = get_logger(__name__)


class ChatGPTClient:
    """ChatGPT API client for generating email responses."""
    
    def __init__(self, api_key: str, model: str = CHATGPT_MODEL):
        """Initialize ChatGPT client."""
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = CHATGPT_SYSTEM_PROMPT + f"\n\nAlways sign emails with:\n{EMAIL_SIGNATURE}"
    
    def generate_response(self, customer_message: str, thread_context: Optional[str] = None) -> str:
        """Generate an email response based on customer message and thread context."""
        user_prompt = f"Current Customer Message:\n{customer_message}\n\n"
        
        if thread_context:
            user_prompt += f"Conversation History:\n{thread_context}\n\n"
        
        user_prompt += "Write a professional and personalized email response below:"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=CHATGPT_TEMPERATURE,
                max_tokens=CHATGPT_MAX_TOKENS
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Error generating ChatGPT response: {e}", exc_info=True, extra={
                "model": self.model,
                "has_context": bool(thread_context)
            })
            return ""
    
    def check_zoom_mention(self, text: str) -> bool:
        """Check if text mentions Zoom meeting confirmation."""
        zoom_keywords = ZOOM_CONFIRMATION_KEYWORDS
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in zoom_keywords)