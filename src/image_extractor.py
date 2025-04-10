"""Image Data Extractor.

A companion to the Meta Prompt Generator that extracts data from images
using the prompts generated by the Meta Prompt Generator.
"""

import os
import sys
import base64
import json
import logging
import requests
from io import BytesIO
from typing import Dict, Any, Optional, List, Tuple
import gradio as gr
from PIL import Image

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.config import OPENROUTER_API_KEY
from src.prompt_generator import MetaPromptGenerator
from src.llm_client import LLMClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageExtractor:
    """Extract data from images using LLMs."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Image Extractor.
        
        Args:
            api_key: API key for OpenRouter
        """
        self.api_key = api_key or OPENROUTER_API_KEY
        self.llm_client = LLMClient(api_key=self.api_key)
        self.prompt_generator = MetaPromptGenerator(llm_client=self.llm_client)
        
        # Available models with vision capabilities
        self.vision_models = {
            "Google Gemini 2.5 Pro": {
                "id": "google/gemini-2.5-pro-exp-03-25:free",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "max_tokens": 4096
            },
            "Quasar Alpha": {
                "id": "openrouter/quasar-alpha",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "max_tokens": 4096
            },
            "DeepSeek Chat v3": {
                "id": "deepseek/deepseek-chat-v3-0324:free",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "max_tokens": 4096
            },
            "Meta Llama 4 Maverick": {
                "id": "meta-llama/llama-4-maverick:free",
                "api_url": "https://openrouter.ai/api/v1/chat/completions",
                "max_tokens": 4096
            }
        }
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image as base64.
        
        Args:
            image_path: Path to the image
            
        Returns:
            Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _get_pil_image_base64(self, pil_image: Image.Image) -> str:
        """Convert PIL Image to base64.
        
        Args:
            pil_image: PIL Image
            
        Returns:
            Base64 encoded image
        """
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def extract_data(self, image: Image.Image, extraction_prompt: str, model_name: str, temperature: float = 0.5) -> Dict[str, Any]:
        """Extract data from an image using an LLM.
        
        Args:
            image: PIL Image to extract data from
            extraction_prompt: Prompt to guide extraction
            model_name: Name of the model to use
            temperature: Temperature for generation
            
        Returns:
            Extracted data
        """
        try:
            # Get the model details
            if model_name not in self.vision_models:
                raise ValueError(f"Model '{model_name}' not found")
                
            model_details = self.vision_models[model_name]
            model_id = model_details["id"]
            api_url = model_details["api_url"]
            max_tokens = model_details["max_tokens"]
            
            # Prepare the image for the API request
            image_base64 = self._get_pil_image_base64(image)
            
            # Replace {file_content} with a reference to the image
            system_message = "You are a helpful assistant that extracts data from images."
            
            # Create the payload for the API request
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": [
                        {"type": "text", "text": extraction_prompt.replace("{file_content}", "the image I'm providing")},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Set up headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://meta-prompt-generator.example.com",
                "X-Title": "Meta Prompt Image Extractor"
            }
            
            # Make the API request
            logger.info(f"Sending request to {api_url} with model {model_id}")
            response = requests.post(
                api_url,
                headers=headers,
                json=payload
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            response_data = response.json()
            
            # Extract the text from the response
            if 'choices' in response_data and len(response_data['choices']) > 0:
                extracted_text = response_data['choices'][0]['message']['content']
                logger.info("Successfully extracted data from image")
                
                # Try to parse JSON from the extracted text
                try:
                    # Find JSON content in the extracted text
                    json_start = extracted_text.find('{')
                    json_end = extracted_text.rfind('}') + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = extracted_text[json_start:json_end]
                        extracted_data = json.loads(json_str)
                        return {
                            "status": "success",
                            "data": extracted_data,
                            "raw_response": extracted_text
                        }
                    else:
                        return {
                            "status": "success",
                            "data": extracted_text,
                            "raw_response": extracted_text
                        }
                except json.JSONDecodeError:
                    logger.warning("Could not parse JSON from extracted text")
                    return {
                        "status": "success",
                        "data": extracted_text,
                        "raw_response": extracted_text
                    }
            else:
                logger.error("Unexpected response format")
                return {
                    "status": "error",
                    "message": "Unexpected response format from API",
                    "raw_response": response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling API: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            
            return {
                "status": "error",
                "message": f"API Error: {str(e)}",
                "raw_response": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                "status": "error",
                "message": f"Error: {str(e)}",
                "raw_response": str(e)
            }

# Function for Gradio UI
def extract_data_from_image(image: Image.Image, extraction_task: str, model_name: str, temperature: float = 0.5) -> Tuple[str, str]:
    """Extract data from an image for the Gradio UI.
    
    Args:
        image: Image to extract data from
        extraction_task: Description of the extraction task
        model_name: Model to use
        temperature: Temperature for generation
        
    Returns:
        Tuple of (generated prompt, extracted data)
    """
    try:
        # Initialize the extractor
        extractor = ImageExtractor()
        
        # Generate the extraction prompt
        prompt_generator = MetaPromptGenerator()
        extraction_prompt = prompt_generator.generate_extraction_prompt(extraction_task)
        
        # Extract data from the image
        result = extractor.extract_data(image, extraction_prompt, model_name, temperature)
        
        # Format the output
        if result["status"] == "success":
            if isinstance(result["data"], dict):
                formatted_data = json.dumps(result["data"], indent=2)
            else:
                formatted_data = result["data"]
                
            return extraction_prompt, formatted_data
        else:
            return extraction_prompt, f"Error: {result['message']}\n\nRaw response: {result['raw_response']}"
    
    except Exception as e:
        logger.error(f"Error in extract_data_from_image: {str(e)}")
        return f"Error generating prompt: {str(e)}", f"Error: {str(e)}"

# Function to create the Gradio UI
def create_ui():
    """Create the Gradio UI for the Image Extractor."""
    
    # Initialize the extractor to get the model list
    extractor = ImageExtractor()
    model_list = list(extractor.vision_models.keys())
    
    # Example extraction tasks
    example_tasks = [
        "Extract invoice details including invoice number, date, total amount, and vendor name",
        "Extract all text from the image and organize it by sections",
        "Extract information from a business card including name, company, position, phone, and email",
        "Extract all product names and prices from a receipt",
        "Extract table data and format it as a structured array"
    ]
    
    # Create the UI
    with gr.Blocks(title="Image Data Extractor", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # Image Data Extractor
            
            Extract structured data from images using prompts generated by the Meta Prompt Generator.
            Upload an image, describe what data you want to extract, select a model, and get the results.
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                # Input components
                input_image = gr.Image(
                    label="Upload Image",
                    type="pil",
                    height=400
                )
                
                extraction_task = gr.Textbox(
                    label="Describe the extraction task",
                    placeholder="E.g., Extract invoice details including invoice number, date, total amount, and vendor name",
                    lines=3
                )
                
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        label="Model",
                        choices=model_list,
                        value=model_list[0] if model_list else None,
                        info="Select the vision model to use"
                    )
                    
                    temperature_slider = gr.Slider(
                        label="Temperature",
                        minimum=0.0,
                        maximum=1.0,
                        value=0.3,
                        step=0.1,
                        info="Lower = more precise, higher = more creative"
                    )
                
                # Extract button
                extract_button = gr.Button("Extract Data", variant="primary")
                
                # Examples
                gr.Examples(
                    examples=example_tasks,
                    inputs=extraction_task,
                    label="Example Tasks"
                )
            
            with gr.Column(scale=1):
                # Output components
                with gr.Accordion("Generated Prompt", open=False):
                    prompt_output = gr.Textbox(
                        label="Generated Prompt",
                        lines=10,
                        show_copy_button=True
                    )
                
                extracted_data = gr.Textbox(
                    label="Extracted Data",
                    lines=20,
                    show_copy_button=True
                )
        
        # Help section
        with gr.Accordion("How to Use", open=False):
            gr.Markdown(
                """
                ## How to Use the Image Data Extractor
                
                1. **Upload an Image**: Click on the upload area to select an image file or drag and drop
                2. **Describe the Extraction Task**: Specify what data you want to extract from the image
                3. **Select a Model**: Choose from different vision-capable LLMs
                4. **Adjust Temperature**: Set the temperature parameter (lower for more precise results)
                5. **Extract Data**: Click the "Extract Data" button
                
                The system will:
                1. Generate an extraction prompt using the Meta Prompt Generator
                2. Send the image and prompt to the selected LLM
                3. Display the extracted data in a structured format
                
                ### Tips for Better Results
                
                - Be specific about what data you want to extract
                - For structured data like invoices, specify the fields you need
                - For tables, mention that you want the data in a structured format
                - If the results aren't ideal, try a different model or adjust the temperature
                """
            )
        
        # Set up the event handlers
        extract_button.click(
            fn=extract_data_from_image,
            inputs=[input_image, extraction_task, model_dropdown, temperature_slider],
            outputs=[prompt_output, extracted_data]
        )
    
    return demo

if __name__ == "__main__":
    # Create and launch the UI
    demo = create_ui()
    demo.launch(share=True)
