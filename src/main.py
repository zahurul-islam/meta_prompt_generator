"""Main application module for the Meta Prompt Generator."""

import logging
import argparse
from typing import Dict, Any

from src.prompt_generator import MetaPromptGenerator
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Meta Prompt Generator for data extraction tasks")
    parser.add_argument(
        "--query", 
        type=str, 
        help="User query for prompt generation"
    )
    parser.add_argument(
        "--temperature", 
        type=float, 
        default=0.5, 
        help="Temperature for LLM generation (0.0-1.0)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="prompt_output.txt", 
        help="Output file for the generated prompt"
    )
    return parser.parse_args()

def main():
    """Run the Meta Prompt Generator."""
    args = parse_args()
    
    # Initialize the LLM client and Meta Prompt Generator
    llm_client = LLMClient()
    generator = MetaPromptGenerator(llm_client=llm_client)
    
    if args.query:
        # Generate the prompt from command line argument
        user_query = args.query
    else:
        # Interactive mode
        print("Welcome to the Meta Prompt Generator!")
        print("Please describe the data extraction task you need a prompt for:")
        user_query = input("> ")
    
    try:
        # Generate the extraction prompt
        generated_prompt = generator.generate_extraction_prompt(user_query)
        
        # Post-process the prompt
        final_prompt = generator.post_process_prompt(generated_prompt)
        
        # Print the generated prompt
        print("\n" + "="*50)
        print("Generated Prompt:")
        print("="*50)
        print(final_prompt)
        print("="*50)
        
        # Save the prompt to a file
        with open(args.output, "w") as f:
            f.write(final_prompt)
        logger.info(f"Prompt saved to {args.output}")
        
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
