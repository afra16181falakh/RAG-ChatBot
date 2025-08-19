import os
import logging
import google.generativeai as genai
from typing import List, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIManager:
    def __init__(self):
        """Initialize API manager with multiple API keys"""
        self.api_keys = [
            os.getenv("GOOGLE_API_KEY_1", ""),
            os.getenv("GOOGLE_API_KEY_2", ""),
            os.getenv("GOOGLE_API_KEY_3", ""),
            os.getenv("GOOGLE_API_KEY_4", ""),
            os.getenv("GOOGLE_API_KEY_5", ""),
        ]
        
        # Filter out empty keys
        self.api_keys = [key for key in self.api_keys if key]
        
        if not self.api_keys:
            # Fallback to single key if no multi-keys provided
            self.api_keys = [os.getenv("GOOGLE_API_KEY", "")]
        
        self.current_key_index = 0
        self.failed_keys = set()
        self.last_reset_time = time.time()
        
    def get_working_key(self) -> Optional[str]:
        """Get the next working API key"""
        # Reset failed keys every hour
        if time.time() - self.last_reset_time > 3600:
            self.failed_keys.clear()
            self.last_reset_time = time.time()
        
        # Try keys in order
        for i, key in enumerate(self.api_keys):
            if key not in self.failed_keys:
                self.current_key_index = i
                return key
        
        # If all keys failed, reset and try again
        self.failed_keys.clear()
        if self.api_keys:
            self.current_key_index = 0
            return self.api_keys[0]
        
        return None
    
    def mark_key_failed(self, key: str):
        """Mark an API key as failed"""
        self.failed_keys.add(key)
        logger.warning(f"API key marked as failed: {key[:10]}...")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using available API keys with automatic failover"""
        max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            key = self.get_working_key()
            if not key:
                return "No API keys available. Please check your configuration."
            
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-1.5-pro")
                
                response = model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                logger.error(f"API key failed: {key[:10]}... Error: {str(e)}")
                self.mark_key_failed(key)
                
                if attempt == max_retries - 1:
                    return "All API keys have failed. Please try again later."
                
                # Wait a bit before retrying with next key
                time.sleep(1)
                continue
        
        return "Unable to generate response. Please try again."

# Global API manager instance
api_manager = APIManager()
