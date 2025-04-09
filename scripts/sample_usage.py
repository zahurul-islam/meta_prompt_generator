#!/usr/bin/env python
"""Sample usage script for the Meta Prompt Generator."""

import os
import sys
import argparse
import requests
import json

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def call_api(query, api_url="http://localhost:8000"):
    """Call the Meta Prompt Generator API.
    
    Args:
        query: User query for prompt generation
        api_url: API URL
        
    Returns:
        Generated prompt
    """
    # Create the request payload
    payload = {
        "query": query,
        "temperature": 0.5
    }
    
    # Call the API
    try:
        response = requests.post(
            f"{api_url}/generate-prompt",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        return data["prompt"]
    
    except requests.exceptions.RequestException as e:
        print(f"Error calling API: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        sys.exit(1)

def main():
    """Run the sample usage script."""
    parser = argparse.ArgumentParser(description="Sample usage of Meta Prompt Generator")
    parser.add_argument(
        "--query", 
        type=str, 
        default="Extract total gross, total net, business name and a list of items including product name and price data as a JSON structure",
        help="User query for prompt generation"
    )
    parser.add_argument(
        "--api-url", 
        type=str, 
        default="http://localhost:8000", 
        help="API URL"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="generated_prompt.txt", 
        help="Output file for the generated prompt"
    )
    args = parser.parse_args()
    
    # Display user query
    print(f"\nGenerating prompt for query: {args.query}\n")
    
    # Call the API
    prompt = call_api(args.query, args.api_url)
    
    # Print the generated prompt
    print("="*50)
    print("Generated Prompt:")
    print("="*50)
    print(prompt)
    print("="*50)
    
    # Save the prompt to a file
    with open(args.output, "w") as f:
        f.write(prompt)
    print(f"\nPrompt saved to {args.output}")

if __name__ == "__main__":
    main()
