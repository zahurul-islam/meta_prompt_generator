"""Client for interacting with LLM APIs."""

import json
import requests
import logging
from typing import Dict, List, Any, Optional

from src.config import OPENROUTER_API_KEY, OPENROUTER_URL, OPENROUTER_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with OpenRouter API to access Qusera Alpha LLM."""
    
    def __init__(self, api_key: str = OPENROUTER_API_KEY, 
                 api_url: str = OPENROUTER_URL,
                 model: str = OPENROUTER_MODEL):
        """Initialize the LLM client.
        
        Args:
            api_key: OpenRouter API key
            api_url: OpenRouter API URL
            model: Model ID for Qusera Alpha LLM
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://meta-prompt-generator.example.com",  # Required by OpenRouter
            "X-Title": "Meta Prompt Generator"  # Application name for OpenRouter
        }
        logger.info(f"Initialized LLM client with model: {self.model}")
        logger.info(f"API URL: {self.api_url}")
        # Log a masked version of the API key for debugging
        masked_key = self.api_key[:5] + "..." + self.api_key[-5:] if len(self.api_key) > 10 else "***"
        logger.info(f"Using API key: {masked_key}")
    
    def generate_prompt(self, system_message: str, user_query: str, 
                        temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """Generate a prompt using the LLM.
        
        Args:
            system_message: System message to guide LLM behavior
            user_query: User request for prompt generation
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated prompt as a string
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_query}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"Sending request to OpenRouter API with model: {self.model}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            # Log the response status and headers for debugging
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Error response from OpenRouter API: {response.text}")
                
                if response.status_code == 400:
                    logger.error("Bad Request: The request was invalid. Check the model name and request format.")
                elif response.status_code == 401:
                    logger.error("Unauthorized: API key is invalid or missing.")
                elif response.status_code == 404:
                    logger.error("Not Found: The requested model might not exist.")
                elif response.status_code == 429:
                    logger.error("Too Many Requests: Rate limit exceeded.")
                elif response.status_code >= 500:
                    logger.error("Server Error: OpenRouter service might be experiencing issues.")
                
                # Return a fallback response in case of error
                return f"Error generating prompt: {response.status_code} - {response.text}"
            
            response_data = response.json()
            logger.debug(f"Response data: {json.dumps(response_data, indent=2)}")
            
            # Extract the generated text from the response
            if 'choices' in response_data and len(response_data['choices']) > 0:
                generated_text = response_data['choices'][0]['message']['content']
                return generated_text
            else:
                logger.error("Unexpected response format: 'choices' missing or empty")
                return "Error: Unexpected response format from OpenRouter API"
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling OpenRouter API: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing OpenRouter API response: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
