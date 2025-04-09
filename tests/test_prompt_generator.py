"""Test the Meta Prompt Generator."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.prompt_generator import MetaPromptGenerator

class TestMetaPromptGenerator(unittest.TestCase):
    """Test the Meta Prompt Generator."""

    def setUp(self):
        """Set up the test environment."""
        self.mock_llm_client = Mock()
        self.generator = MetaPromptGenerator(llm_client=self.mock_llm_client)
        
        # Create mock templates for testing
        os.makedirs(self.generator.template_dir, exist_ok=True)

    def test_enhance_user_query(self):
        """Test the query enhancement method."""
        test_query = "Extract invoice details"
        enhanced_query = self.generator._enhance_user_query(test_query)
        
        # Check that the enhanced query includes the original query
        self.assertIn(test_query, enhanced_query)
        
        # Check that the enhanced query includes instructions about file_content
        self.assertIn("{file_content}", enhanced_query)
        
        # Check that the enhanced query includes guidance on output format
        self.assertIn("JSON", enhanced_query)

    @patch('src.prompt_generator.MetaPromptGenerator._try_with_backup_models')
    def test_generate_extraction_prompt(self, mock_try_with_backup_models):
        """Test the prompt generation method."""
        # Set up the mock return values
        self.mock_llm_client.generate_prompt.return_value = """
        You are a data extraction assistant. Your task is to analyze the provided document in {file_content} and extract the following information:

        1. Invoice number
        2. Total amount
        3. Date of invoice
        
        Please format your response as a JSON object.
        """
        
        # Mock behavior to return the original prompt directly
        mock_try_with_backup_models.return_value = "Backup model response"
        
        test_query = "Extract invoice number, total, and date"
        result = self.generator.generate_extraction_prompt(test_query)
        
        # Check that the LLM client was called
        self.mock_llm_client.generate_prompt.assert_called_once()
        
        # Check that the result includes file_content variable
        self.assertIn("{file_content}", result)
        
        # Check that JSON formatting is mentioned
        self.assertIn("JSON", result)
        
        # Test error handling path
        self.mock_llm_client.generate_prompt.side_effect = Exception("Test error")
        result = self.generator.generate_extraction_prompt(test_query)
        
        # Should call the backup method when an error occurs
        mock_try_with_backup_models.assert_called_once()

    def test_post_process_prompt(self):
        """Test the post-processing of prompts."""
        # Test case 1: Prompt already includes {file_content}
        prompt_with_var = "Analyze the document in {file_content} and extract data."
        result = self.generator.post_process_prompt(prompt_with_var)
        self.assertEqual(result, prompt_with_var)
        
        # Test case 2: Prompt uses "the document" but no variable
        prompt_without_var = "Analyze the document and extract data."
        result = self.generator.post_process_prompt(prompt_without_var)
        self.assertIn("{file_content}", result)
        
        # Test case 3: Prompt uses "the input document" but no variable
        prompt_alt_phrase = "Analyze the input document and extract data."
        result = self.generator.post_process_prompt(prompt_alt_phrase)
        self.assertIn("{file_content}", result)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Template content")
    def test_load_template(self, mock_open, mock_exists):
        """Test the template loading functionality."""
        # Mock the exists check to return True
        mock_exists.return_value = True
        
        # Call the method
        template = self.generator._load_template("test_template.txt")
        
        # Check that the result matches the expected content
        self.assertEqual(template, "Template content")
        
        # Check that the method returns None when the template doesn't exist
        mock_exists.return_value = False
        template = self.generator._load_template("nonexistent_template.txt")
        self.assertIsNone(template)

    def test_generate_fallback_prompt(self):
        """Test the fallback prompt generation."""
        # Test with invoice query
        invoice_query = "Extract invoice data with total and date"
        with patch.object(self.generator, '_load_template', return_value="Invoice template content"):
            result = self.generator._generate_fallback_prompt(invoice_query)
            self.assertEqual(result, "Invoice template content")
        
        # Test with email query
        email_query = "Extract email sender and subject"
        with patch.object(self.generator, '_load_template', return_value="Email template content"):
            result = self.generator._generate_fallback_prompt(email_query)
            self.assertEqual(result, "Email template content")
        
        # Test with legal document query
        legal_query = "Extract contract terms and parties"
        with patch.object(self.generator, '_load_template', return_value="Legal template content"):
            result = self.generator._generate_fallback_prompt(legal_query)
            self.assertEqual(result, "Legal template content")
        
        # Test with generic query (no specific template)
        generic_query = "Extract data from document"
        with patch.object(self.generator, '_load_template', return_value=None):
            result = self.generator._generate_fallback_prompt(generic_query)
            self.assertIn(generic_query, result)
            self.assertIn("{file_content}", result)

if __name__ == '__main__':
    unittest.main()
