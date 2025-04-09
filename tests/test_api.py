"""Test the FastAPI application."""

import os
import sys
import json
from fastapi.testclient import TestClient
from unittest.mock import patch

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.api import app

client = TestClient(app)

class TestAPI:
    """Test the API endpoints."""

    @patch('src.prompt_generator.MetaPromptGenerator.generate_extraction_prompt')
    def test_generate_prompt_endpoint(self, mock_generate_prompt):
        """Test the generate-prompt endpoint."""
        # Set up the mock return value
        mock_generate_prompt.return_value = """
        You are a data extraction assistant. Your task is to analyze the document provided in {file_content} and extract:
        
        1. Invoice number
        2. Total amount
        3. Date
        
        Format as JSON:
        {
            "invoice_number": "value",
            "total_amount": number,
            "date": "YYYY-MM-DD"
        }
        """
        
        # Create a test request
        test_request = {
            "query": "Extract invoice number, total amount, and date",
            "temperature": 0.5
        }
        
        # Make the request
        response = client.post("/generate-prompt", json=test_request)
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "prompt" in data
        assert "{file_content}" in data["prompt"]
        assert "metadata" in data
        assert data["metadata"]["query"] == test_request["query"]
        assert data["metadata"]["temperature"] == test_request["temperature"]
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    @patch('src.prompt_generator.MetaPromptGenerator.generate_extraction_prompt')
    def test_error_handling(self, mock_generate_prompt):
        """Test error handling in the API."""
        # Make the mock raise an exception
        mock_generate_prompt.side_effect = Exception("Test error")
        
        # Create a test request
        test_request = {
            "query": "Extract invoice data",
            "temperature": 0.5
        }
        
        # Make the request
        response = client.post("/generate-prompt", json=test_request)
        
        # Check the response
        assert response.status_code == 500
        assert "detail" in response.json()
        assert "Test error" in response.json()["detail"]
