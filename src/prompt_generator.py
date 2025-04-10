"""Meta Prompt Generator for data extraction tasks."""

import logging
import json
import os
import random
from typing import Dict, List, Any, Optional

from src.config import META_SYSTEM_MESSAGE, TEMPLATE_DIR, BACKUP_MODELS
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaPromptGenerator:
    """Generate data extraction prompts based on user request."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the Meta Prompt Generator.
        
        Args:
            llm_client: LLM client for generating prompts
        """
        self.llm_client = llm_client or LLMClient()
        self.system_message = META_SYSTEM_MESSAGE
        self.template_dir = TEMPLATE_DIR
        
        # Create template directory if it doesn't exist
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
            logger.info(f"Created template directory: {self.template_dir}")
    
    def _enhance_user_query(self, user_query: str) -> str:
        """Enhance the user query with additional context and instructions.
        
        Args:
            user_query: Original user query
            
        Returns:
            Enhanced user query
        """
        enhanced_query = f"""
I need you to create a detailed prompt for a data extraction task based on the following requirement:

"{user_query}"

The prompt you generate should:
1. Instruct the model to carefully analyze the entire document provided in {{file_content}}
2. Specify all data fields that need to be extracted as mentioned in the requirement
3. Provide clear instructions on the expected output format (JSON)
4. Include guidance on handling missing or unclear information
5. Include at least one example of the expected output format

Please generate the complete prompt that I can use with an LLM to extract the specified data.
"""
        return enhanced_query
    
    def _load_template(self, template_name: str) -> Optional[str]:
        """Load a template from the templates directory.
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            Template content or None if not found
        """
        template_path = os.path.join(self.template_dir, template_name)
        
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                content = f.read()
            logger.info(f"Loaded template: {template_name}")
            return content
        
        return None
    
    def _generate_fallback_prompt(self, user_query: str) -> str:
        """Generate a fallback prompt if the LLM request fails.
        
        Args:
            user_query: User request for data extraction prompt
            
        Returns:
            Fallback prompt
        """
        logger.info("Generating fallback prompt based on templates")
        
        # Determine the type of extraction task
        query_lower = user_query.lower()
        
        if "invoice" in query_lower or "bill" in query_lower or "receipt" in query_lower:
            template = self._load_template("invoice_template.txt")
            if template:
                return template
                
        elif "email" in query_lower or "message" in query_lower:
            template = self._load_template("email_template.txt")
            if template:
                return template
                
        elif "legal" in query_lower or "contract" in query_lower or "agreement" in query_lower:
            template = self._load_template("legal_template.txt")
            if template:
                return template
        
        # If no specific template matches, create a generic one
        return f"""You are a data extraction assistant. Your task is to carefully analyze the document provided in {{file_content}} and extract the following information in a structured JSON format:

{user_query}

Format your response as a JSON object with the appropriate structure for the requested data.

Guidelines:
1. If certain information is not present in the document, use null for that field or omit the field entirely.
2. Convert all monetary values to numbers (not strings).
3. Use consistent date formatting (DD-MM-YYYY).
4. If you're uncertain about any information, include a "confidence" field with a value between 0 and 1.
5. Extract the data exactly as it appears without making assumptions or adding information not present in the document.
6. Only include the JSON in your response, with no additional explanation or commentary.
"""
    
    def _try_with_backup_models(self, user_query: str) -> str:
        """Try generating a prompt with backup models.
        
        Args:
            user_query: Enhanced user query
            
        Returns:
            Generated prompt or fallback prompt if all models fail
        """
        original_model = self.llm_client.model
        
        for model in BACKUP_MODELS:
            if model == original_model:
                continue
                
            logger.info(f"Trying backup model: {model}")
            
            try:
                # Update the model
                self.llm_client.model = model
                
                # Generate the prompt
                generated_prompt = self.llm_client.generate_prompt(
                    system_message=self.system_message,
                    user_query=user_query,
                    temperature=0.5
                )
                
                if "Error generating prompt" not in generated_prompt:
                    logger.info(f"Successfully generated prompt with backup model: {model}")
                    return generated_prompt
                
            except Exception as e:
                logger.error(f"Error with backup model {model}: {str(e)}")
        
        # Reset to original model
        self.llm_client.model = original_model
        
        # Return a fallback prompt
        return self._generate_fallback_prompt(user_query)
        
    def generate_extraction_prompt(self, user_query: str) -> str:
        """Generate a data extraction prompt based on user request.
        
        Args:
            user_query: User request for data extraction prompt
            
        Returns:
            Generated data extraction prompt
        """
        # Enhance the user query with additional context
        enhanced_query = self._enhance_user_query(user_query)
        
        # Generate the prompt using the LLM
        logger.info("Generating extraction prompt...")
        try:
            generated_prompt = self.llm_client.generate_prompt(
                system_message=self.system_message,
                user_query=enhanced_query,
                temperature=0.5  # Lower temperature for more consistent output
            )
            
            # Check if there was an error
            if "Error generating prompt" in generated_prompt:
                logger.warning("Primary model returned an error, trying backup models")
                generated_prompt = self._try_with_backup_models(enhanced_query)
            
            logger.info("Extraction prompt generated successfully")
            return generated_prompt
            
        except Exception as e:
            logger.error(f"Error generating prompt: {str(e)}")
            return self._try_with_backup_models(enhanced_query)

    def post_process_prompt(self, prompt: str) -> str:
        """Post-process the generated prompt.
        
        Args:
            prompt: Generated prompt
            
        Returns:
            Post-processed prompt
        """
        # Ensure the prompt includes {file_content} as a variable
        if "{file_content}" not in prompt:
            prompt = prompt.replace("the document", "the document provided in {file_content}")
            prompt = prompt.replace("the input document", "the input document provided in {file_content}")
            prompt = prompt.replace("the provided document", "the provided document in {file_content}")
        
        return prompt
